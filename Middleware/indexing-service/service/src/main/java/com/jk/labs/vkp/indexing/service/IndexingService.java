package com.jk.labs.vkp.indexing.service;

import com.jk.labs.vkp.indexing.common.dto.admin.CredentialDTO;
import com.jk.labs.vkp.indexing.common.dto.admin.FormulaDTO;
import com.jk.labs.vkp.indexing.common.dto.admin.IndexLogDTO;
import com.jk.labs.vkp.indexing.common.dto.admin.WorkflowDTO;
import com.jk.labs.vkp.indexing.common.dto.callback.IndexCallbackCtx;
import com.jk.labs.vkp.indexing.common.dto.callback.IndexCallbackReqDTO;
import com.jk.labs.vkp.indexing.common.dto.callback.IndexCallbackRespDTO;
import com.jk.labs.vkp.indexing.common.dto.trigger.TriggerIndexCtx;
import com.jk.labs.vkp.indexing.common.dto.trigger.TriggerIndexReqDTO;
import com.jk.labs.vkp.indexing.common.dto.trigger.TriggerIndexRespDTO;
import com.jk.labs.vkp.indexing.common.enums.IndexStatus;
import com.jk.labs.vkp.indexing.common.enums.WfType;
import com.jk.labs.vkp.indexing.common.error.ResourceNotFoundException;
import com.jk.labs.vkp.indexing.dao.entity.IndexFormulaEntity;
import com.jk.labs.vkp.indexing.dao.entity.IndexingWorkflowEntity;
import com.jk.labs.vkp.indexing.dao.entity.ProviderCredentialEntity;
import com.jk.labs.vkp.indexing.dao.entity.ResourceGraphIndexLogEntity;
import com.jk.labs.vkp.indexing.dao.repository.IndexFormulaRepository;
import com.jk.labs.vkp.indexing.dao.repository.IndexingWorkflowRepository;
import com.jk.labs.vkp.indexing.dao.repository.ProviderCredentialRepository;
import com.jk.labs.vkp.indexing.dao.repository.ResourceGraphIndexLogRepository;
import com.jk.labs.vkp.indexing.utils.AuditUtils;
import com.jk.labs.vkp.indexing.utils.IdGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;

/**
 * Indexing control plane: registry reads + the trigger (dedup + route to AIRFLOW or
 * SPRING_AI executors) + the executor callback. It never embeds — it orchestrates.
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class IndexingService {

    private static final List<String> ACTIVE_STATES =
            List.of(IndexStatus.PENDING.name(), IndexStatus.IN_PROGRESS.name(), IndexStatus.INDEXED.name());

    private final IndexingWorkflowRepository workflowRepo;
    private final IndexFormulaRepository formulaRepo;
    private final ProviderCredentialRepository credentialRepo;
    private final ResourceGraphIndexLogRepository logRepo;
    private final WfsClient wfsClient;
    private final AirflowAdapterClient adapterClient;
    private final IndexingProperties props;

    // ---- registry reads ----
    public List<WorkflowDTO> listWorkflows() {
        return workflowRepo.findAll().stream().map(IndexingService::toWf).toList();
    }

    public List<FormulaDTO> listFormulas() {
        return formulaRepo.findAll().stream().map(IndexingService::toFormula).toList();
    }

    public List<CredentialDTO> listCredentials() {
        return credentialRepo.findAll().stream().map(IndexingService::toCred).toList();
    }

    public List<IndexLogDTO> listLogs(String companyId) {
        return logRepo.findByCompanyIdOrderByCreatedDtDesc(companyId).stream().map(IndexingService::toLog).toList();
    }

    // ---- trigger ----
    @Transactional
    public void trigger(TriggerIndexCtx ctx) {
        TriggerIndexReqDTO req = ctx.getReqDTO();
        String actor = AuditUtils.actorOrDefault(req.getTriggeredBy());

        IndexingWorkflowEntity wf = workflowRepo.findById(req.getWfId())
                .orElseThrow(() -> new ResourceNotFoundException("Workflow not found: " + req.getWfId()));
        IndexFormulaEntity formula = formulaRepo.findById(req.getIndexFormulaId())
                .orElseThrow(() -> new ResourceNotFoundException("Index formula not found: " + req.getIndexFormulaId()));

        // dedup: an equivalent (company, workflow, formula) run already pending/running/indexed
        if (!req.isForce()) {
            List<ResourceGraphIndexLogEntity> existing = logRepo
                    .findByCompanyIdAndWfIdAndIndexFormulaIdAndStatusIn(
                            req.getCompanyId(), wf.getWfId(), formula.getIndexFormulaId(), ACTIVE_STATES);
            if (!existing.isEmpty()) {
                ResourceGraphIndexLogEntity e = existing.get(0);
                ctx.setRespDTO(new TriggerIndexRespDTO(e.getIndexLogId(), e.getWfType(), e.getStatus(),
                        e.getRunRef(), true, "Equivalent run already exists (force=true to re-run)"));
                return;
            }
        }

        String scope = (req.getDocIds() == null || req.getDocIds().isEmpty()) ? "WHOLE" : "SELECTED";
        int docCount = "SELECTED".equals(scope) ? req.getDocIds().size() : 0;
        String indexedTo = formula.getVectorStore() != null ? formula.getVectorStore() : props.getDefaultVectorStore();
        String vectorTarget = "vec_" + sanitize(formula.getEmbeddingModel());
        Instant now = Instant.now();
        String logId = IdGenerator.newId();

        ResourceGraphIndexLogEntity logRow = ResourceGraphIndexLogEntity.builder()
                .indexLogId(logId).companyId(req.getCompanyId())
                .wfId(wf.getWfId()).wfType(wf.getWfType())
                .indexFormulaId(formula.getIndexFormulaId())
                .provider(formula.getEmbeddingProvider()).embeddingModel(formula.getEmbeddingModel())
                .indexedTo(indexedTo).providerCredentialId(req.getProviderCredentialId()).vectorTarget(vectorTarget)
                .scope(scope).docCount(docCount)
                .status(IndexStatus.PENDING.name()).version("1")
                .createdDt(now).updatedDt(now).createdBy(actor).updatedBy(actor)
                .build();
        logRepo.save(logRow);

        String runRef;
        if (WfType.SPRING_AI.name().equals(wf.getWfType())) {
            runRef = "wfs-" + logId;
            markInProgress(logRow, runRef, now);
            try {
                java.util.Map<String, Object> rp = new java.util.LinkedHashMap<>();
                rp.put("companyId", req.getCompanyId());
                rp.put("companyName", req.getCompanyName());
                rp.put("scope", scope);
                rp.put("docIds", req.getDocIds() == null ? List.of() : req.getDocIds());
                rp.put("vectorTarget", vectorTarget);
                rp.put("embeddingProvider", formula.getEmbeddingProvider());
                rp.put("embeddingModel", formula.getEmbeddingModel());
                rp.put("indexedTo", indexedTo);
                rp.put("params", formula.getParams());
                wfsClient.execute(wf.getTargetRef(), logId, rp);
            } catch (RuntimeException ex) {
                fail(logRow, ex.getMessage());
                ctx.setRespDTO(new TriggerIndexRespDTO(logId, wf.getWfType(), IndexStatus.FAILED.name(),
                        runRef, false, "Executor unreachable: " + ex.getMessage()));
                return;
            }
        } else { // AIRFLOW
            try {
                java.util.Map<String, Object> conf = new java.util.LinkedHashMap<>();
                conf.put("index_log_id", logId);
                conf.put("company_id", req.getCompanyId());
                conf.put("company_name", req.getCompanyName());
                conf.put("vector_target", vectorTarget);
                conf.put("embedding_provider", formula.getEmbeddingProvider());
                conf.put("embedding_model", formula.getEmbeddingModel());
                conf.put("indexed_to", indexedTo);
                conf.put("mongo_uri", "mongodb://host.docker.internal:27017/vkp?directConnection=true");
                conf.put("params", formula.getParams());
                conf.put("data_collection_base_url", props.getDataCollectionBaseUrl());
                conf.put("callback_base_url", props.getAirflowCallbackBaseUrl());
                conf.put("pg_host", props.getPgHost());
                conf.put("pg_port", props.getPgPort());
                conf.put("pg_db", props.getPgDb());
                conf.put("pg_user", props.getPgUser());
                conf.put("pg_password", props.getPgPassword());
                if (req.getDocIds() != null) {
                    conf.put("doc_ids", req.getDocIds());
                }
                AirflowAdapterClient.DagRunRef run = adapterClient.triggerDag(wf.getTargetRef(), conf, actor);
                runRef = run.dagRunId();
                markInProgress(logRow, runRef, now);
            } catch (RuntimeException ex) {
                fail(logRow, ex.getMessage());
                ctx.setRespDTO(new TriggerIndexRespDTO(logId, wf.getWfType(), IndexStatus.FAILED.name(),
                        "airflow-error", false, "Failed to trigger DAG: " + ex.getMessage()));
                return;
            }
        }

        log.info("Indexing triggered: company={} wf={} ({}) formula={} -> log={}",
                req.getCompanyId(), wf.getName(), wf.getWfType(), formula.getName(), logId);
        ctx.setRespDTO(new TriggerIndexRespDTO(logId, wf.getWfType(), IndexStatus.IN_PROGRESS.name(),
                runRef, false, "Indexing triggered"));
    }

    // ---- executor callback ----
    @Transactional
    public void callback(IndexCallbackCtx ctx) {
        IndexCallbackReqDTO req = ctx.getReqDTO();
        ResourceGraphIndexLogEntity logRow = logRepo.findById(req.getIndexLogId())
                .orElseThrow(() -> new ResourceNotFoundException("Index log not found: " + req.getIndexLogId()));
        logRow.setStatus(req.getStatus());
        if (req.getChunks() != null) {
            logRow.setChunks(req.getChunks());
        }
        if (req.getError() != null) {
            logRow.setError(req.getError());
        }
        if (req.getRunRef() != null) {
            logRow.setRunRef(req.getRunRef());
        }
        if (IndexStatus.INDEXED.name().equals(req.getStatus()) || IndexStatus.FAILED.name().equals(req.getStatus())) {
            logRow.setIndexEndDt(Instant.now());
        }
        logRow.setUpdatedDt(Instant.now());
        logRepo.save(logRow);
        log.info("Index log {} -> {} (chunks={})", logRow.getIndexLogId(), logRow.getStatus(), logRow.getChunks());
        ctx.setRespDTO(new IndexCallbackRespDTO(logRow.getIndexLogId(), logRow.getStatus()));
    }

    private void markInProgress(ResourceGraphIndexLogEntity logRow, String runRef, Instant now) {
        logRow.setStatus(IndexStatus.IN_PROGRESS.name());
        logRow.setRunRef(runRef);
        logRow.setIndexStartDt(now);
        logRow.setUpdatedDt(now);
        logRepo.save(logRow);
    }

    private void fail(ResourceGraphIndexLogEntity logRow, String error) {
        logRow.setStatus(IndexStatus.FAILED.name());
        logRow.setError(error);
        logRow.setIndexEndDt(Instant.now());
        logRow.setUpdatedDt(Instant.now());
        logRepo.save(logRow);
    }

    private static String sanitize(String model) {
        return model == null ? "default" : model.toLowerCase().replaceAll("[^a-z0-9]+", "_");
    }

    // ---- mappers ----
    private static WorkflowDTO toWf(IndexingWorkflowEntity e) {
        return WorkflowDTO.builder().wfId(e.getWfId()).name(e.getName()).wfType(e.getWfType())
                .targetRef(e.getTargetRef()).description(e.getDescription()).status(e.getStatus()).build();
    }

    private static FormulaDTO toFormula(IndexFormulaEntity e) {
        return FormulaDTO.builder().indexFormulaId(e.getIndexFormulaId()).name(e.getName())
                .embeddingProvider(e.getEmbeddingProvider()).embeddingModel(e.getEmbeddingModel())
                .vectorStore(e.getVectorStore())
                .params(e.getParams()).status(e.getStatus()).build();
    }

    private static CredentialDTO toCred(ProviderCredentialEntity e) {
        return CredentialDTO.builder().providerCredentialId(e.getProviderCredentialId())
                .providerType(e.getProviderType()).name(e.getName()).status(e.getStatus()).build();
    }

    private static IndexLogDTO toLog(ResourceGraphIndexLogEntity e) {
        return IndexLogDTO.builder()
                .indexLogId(e.getIndexLogId()).companyId(e.getCompanyId()).resourceGraphId(e.getResourceGraphId())
                .wfId(e.getWfId()).wfType(e.getWfType()).indexFormulaId(e.getIndexFormulaId())
                .provider(e.getProvider()).embeddingModel(e.getEmbeddingModel())
                .indexedTo(e.getIndexedTo()).vectorTarget(e.getVectorTarget())
                .scope(e.getScope()).docCount(e.getDocCount()).status(e.getStatus()).version(e.getVersion())
                .runRef(e.getRunRef()).chunks(e.getChunks()).error(e.getError())
                .indexStartDt(e.getIndexStartDt()).indexEndDt(e.getIndexEndDt())
                .createdDt(e.getCreatedDt()).updatedDt(e.getUpdatedDt()).build();
    }
}
