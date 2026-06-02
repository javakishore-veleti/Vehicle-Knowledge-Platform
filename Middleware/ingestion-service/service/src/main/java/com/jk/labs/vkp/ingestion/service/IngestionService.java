package com.jk.labs.vkp.ingestion.service;

import com.jk.labs.vkp.ingestion.common.dto.content.ContentDTO;
import com.jk.labs.vkp.ingestion.common.dto.content.ContentItemDTO;
import com.jk.labs.vkp.ingestion.common.dto.content.ContentRecordCtx;
import com.jk.labs.vkp.ingestion.common.dto.content.ContentRecordReqDTO;
import com.jk.labs.vkp.ingestion.common.dto.content.ContentRecordRespDTO;
import com.jk.labs.vkp.ingestion.common.dto.content.ListContentCtx;
import com.jk.labs.vkp.ingestion.common.dto.content.ListContentRespDTO;
import com.jk.labs.vkp.ingestion.common.dto.ingest.IngestCtx;
import com.jk.labs.vkp.ingestion.common.dto.ingest.IngestReqDTO;
import com.jk.labs.vkp.ingestion.common.dto.ingest.IngestRespDTO;
import com.jk.labs.vkp.ingestion.common.dto.status.GetStatusCtx;
import com.jk.labs.vkp.ingestion.common.dto.status.GetStatusReqDTO;
import com.jk.labs.vkp.ingestion.common.dto.status.GetStatusRespDTO;
import com.jk.labs.vkp.ingestion.common.dto.workflow.ListWorkflowsCtx;
import com.jk.labs.vkp.ingestion.common.dto.workflow.ListWorkflowsRespDTO;
import com.jk.labs.vkp.ingestion.common.dto.workflow.WorkflowRunDTO;
import com.jk.labs.vkp.ingestion.dao.entity.ContentEntity;
import com.jk.labs.vkp.ingestion.dao.repository.ContentRepository;
import com.jk.labs.vkp.ingestion.service.mapper.ContentMapper;
import com.jk.labs.vkp.ingestion.utils.AuditUtils;
import com.jk.labs.vkp.ingestion.utils.IdGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;

/**
 * Control plane for content ingestion. Triggers the {@code vkp_process_resources} DAG via
 * airflow-adapter-service to crawl discovered links and extract content; persists the
 * extracted content (reported back by the DAG) into company_resource_content.
 * Every method takes only its use case {@code Ctx}.
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class IngestionService {

    private static final String INGEST_DAG_ID = "vkp_process_resources";
    private static final int DEFAULT_LIMIT = 5;
    private static final int MAX_URL_LEN = 1000;
    private static final int MAX_TITLE_LEN = 250;

    private final ContentRepository contentRepository;
    private final AirflowAdapterClient adapterClient;

    /** Where the DAG fetches discovered links from (data-collection-service). */
    @Value("${ingestion.graph-base-url:http://host.docker.internal:8084}")
    private String graphBaseUrl;

    /** Where the DAG posts extracted content back to (this service). */
    @Value("${ingestion.callback-base-url:http://host.docker.internal:8085}")
    private String callbackBaseUrl;

    public void ingest(IngestCtx ctx) {
        IngestReqDTO req = ctx.getReqDTO();
        String actor = AuditUtils.actorOrDefault(req.getTriggeredBy());
        Map<String, Object> conf = new LinkedHashMap<>();
        conf.put("company_id", req.getCompanyId());
        conf.put("company_resource_id", req.getCompanyResourceId());
        conf.put("graph_base_url", graphBaseUrl);
        conf.put("callback_base_url", callbackBaseUrl);
        conf.put("limit", req.getLimit() > 0 ? req.getLimit() : DEFAULT_LIMIT);
        AirflowAdapterClient.DagRunRef run = adapterClient.triggerDag(INGEST_DAG_ID, conf, actor);
        log.info("Ingestion triggered: company={} resource={} -> dagRun={}",
                req.getCompanyId(), req.getCompanyResourceId(), run.dagRunId());
        ctx.setRespDTO(new IngestRespDTO(run.dagId() != null ? run.dagId() : INGEST_DAG_ID,
                run.dagRunId(), run.state()));
    }

    @Transactional
    public void recordContent(ContentRecordCtx ctx) {
        ContentRecordReqDTO req = ctx.getReqDTO();
        Instant now = Instant.now();
        int added = 0;
        for (ContentItemDTO item : req.getItems() == null ? List.<ContentItemDTO>of() : req.getItems()) {
            if (item.getSourceUrl() == null || item.getSourceUrl().isBlank()) {
                continue;
            }
            contentRepository.save(ContentEntity.builder()
                    .contentId(IdGenerator.newId())
                    .companyId(req.getCompanyId())
                    .companyResourceId(req.getCompanyResourceId())
                    .resourceGraphId(item.getResourceGraphId())
                    .sourceUrl(trim(item.getSourceUrl(), MAX_URL_LEN))
                    .title(trim(item.getTitle(), MAX_TITLE_LEN))
                    .cleanText(item.getCleanText())
                    .contentHash(item.getContentHash())
                    .crawlStatus("CRAWLED")
                    .embeddingStatus("PENDING")
                    .createdDt(now).updatedDt(now)
                    .createdBy("airflow").updatedBy("airflow")
                    .build());
            added++;
        }
        log.info("Recorded {} content item(s) for company {}", added, req.getCompanyId());
        ctx.setRespDTO(new ContentRecordRespDTO(added));
    }

    @Transactional(readOnly = true)
    public void listContent(ListContentCtx ctx) {
        String companyId = ctx.getReqDTO().getCompanyId();
        List<ContentDTO> items = contentRepository.findByCompanyId(companyId).stream()
                .map(ContentMapper::toDTO)
                .toList();
        ctx.setRespDTO(new ListContentRespDTO(items, items.size()));
    }

    public void listWorkflows(ListWorkflowsCtx ctx) {
        String dagId = ctx.getReqDTO().getDagId();
        List<WorkflowRunDTO> runs = adapterClient.listRuns(dagId);
        ctx.setRespDTO(new ListWorkflowsRespDTO(runs, runs.size()));
    }

    public void getStatus(GetStatusCtx ctx) {
        GetStatusReqDTO req = ctx.getReqDTO();
        AirflowAdapterClient.DagRunRef run = adapterClient.getRun(req.getDagId(), req.getRunId());
        ctx.setRespDTO(new GetStatusRespDTO(run.dagId() != null ? run.dagId() : req.getDagId(),
                run.dagRunId(), run.state()));
    }

    private static String trim(String value, int max) {
        return value == null ? null : (value.length() > max ? value.substring(0, max) : value);
    }
}
