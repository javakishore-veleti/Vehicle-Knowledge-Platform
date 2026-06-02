package com.jk.labs.vkp.datacollection.service;

import com.jk.labs.vkp.datacollection.common.dto.discover.DiscoverCtx;
import com.jk.labs.vkp.datacollection.common.dto.discover.DiscoverReqDTO;
import com.jk.labs.vkp.datacollection.common.dto.discover.DiscoverRespDTO;
import com.jk.labs.vkp.datacollection.common.dto.discover.RecordDiscoveredCtx;
import com.jk.labs.vkp.datacollection.common.dto.discover.RecordDiscoveredReqDTO;
import com.jk.labs.vkp.datacollection.common.dto.discover.RecordDiscoveredRespDTO;
import com.jk.labs.vkp.datacollection.common.dto.graph.GetGraphCtx;
import com.jk.labs.vkp.datacollection.common.dto.graph.GetGraphRespDTO;
import com.jk.labs.vkp.datacollection.common.dto.graph.ResourceGraphNodeDTO;
import com.jk.labs.vkp.datacollection.common.dto.status.GetStatusCtx;
import com.jk.labs.vkp.datacollection.common.dto.status.GetStatusReqDTO;
import com.jk.labs.vkp.datacollection.common.dto.status.GetStatusRespDTO;
import com.jk.labs.vkp.datacollection.common.dto.workflow.ListWorkflowsCtx;
import com.jk.labs.vkp.datacollection.common.dto.workflow.ListWorkflowsRespDTO;
import com.jk.labs.vkp.datacollection.common.dto.workflow.WorkflowRunDTO;
import com.jk.labs.vkp.datacollection.common.enums.CrawlStatus;
import com.jk.labs.vkp.datacollection.common.enums.Status;
import com.jk.labs.vkp.datacollection.dao.entity.ResourceGraphNodeEntity;
import com.jk.labs.vkp.datacollection.dao.repository.ResourceGraphNodeRepository;
import com.jk.labs.vkp.datacollection.service.mapper.ResourceGraphNodeMapper;
import com.jk.labs.vkp.datacollection.utils.AuditUtils;
import com.jk.labs.vkp.datacollection.utils.IdGenerator;
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
 * Control plane for link discovery. It records the resource-graph root and triggers the
 * {@code vkp_discover_resources} DAG via airflow-adapter-service — it does not crawl itself.
 * Every method takes only its use case {@code Ctx}.
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class DataCollectionService {

    private static final String DISCOVER_DAG_ID = "vkp_discover_resources";
    private static final String SEED_RESOURCE_TYPE = "SEED";
    private static final String LINK_RESOURCE_TYPE = "LINK";
    private static final int MAX_URL_LEN = 1000;

    private final ResourceGraphNodeRepository graphRepository;
    private final AirflowAdapterClient adapterClient;

    /** Base URL the DAG (running in the Airflow container) uses to call back into this service. */
    @Value("${datacollection.callback-base-url:http://host.docker.internal:8084}")
    private String callbackBaseUrl;

    @Transactional
    public void discover(DiscoverCtx ctx) {
        DiscoverReqDTO req = ctx.getReqDTO();
        String actor = AuditUtils.actorOrDefault(req.getTriggeredBy());
        Instant now = Instant.now();

        // 1) record the discovery root in company_resource_graph
        String rootId = IdGenerator.newId();
        ResourceGraphNodeEntity root = ResourceGraphNodeEntity.builder()
                .resourceGraphId(rootId)
                .companyId(req.getCompanyId())
                .companyResourceId(req.getCompanyResourceId())
                .resourceUrl(req.getSeedUrl())
                .resourceType(req.getResourceType() != null ? req.getResourceType() : SEED_RESOURCE_TYPE)
                .crawlStatus(CrawlStatus.DISCOVERING.name())
                .status(Status.DEFAULT)
                .createdDt(now)
                .updatedDt(now)
                .createdBy(actor)
                .updatedBy(actor)
                .build();
        graphRepository.save(root);

        // 2) trigger the discovery DAG through the adapter (no direct Airflow access)
        Map<String, Object> conf = new LinkedHashMap<>();
        conf.put("company_id", req.getCompanyId());
        conf.put("company_resource_id", req.getCompanyResourceId());
        conf.put("seed_url", req.getSeedUrl());
        conf.put("resource_graph_id", rootId);
        conf.put("callback_base_url", callbackBaseUrl);
        AirflowAdapterClient.DagRunRef run = adapterClient.triggerDag(DISCOVER_DAG_ID, conf, actor);

        log.info("Discovery triggered: company={} resource={} -> dagRun={} (graphRoot={})",
                req.getCompanyId(), req.getCompanyResourceId(), run.dagRunId(), rootId);
        ctx.setRespDTO(new DiscoverRespDTO(rootId,
                run.dagId() != null ? run.dagId() : DISCOVER_DAG_ID, run.dagRunId(), run.state()));
    }

    @Transactional
    public void recordDiscovered(RecordDiscoveredCtx ctx) {
        RecordDiscoveredReqDTO req = ctx.getReqDTO();
        Instant now = Instant.now();
        int added = 0;
        for (String url : req.getLinks() == null ? List.<String>of() : req.getLinks()) {
            if (url == null || url.isBlank()) {
                continue;
            }
            String trimmed = url.length() > MAX_URL_LEN ? url.substring(0, MAX_URL_LEN) : url;
            graphRepository.save(ResourceGraphNodeEntity.builder()
                    .resourceGraphId(IdGenerator.newId())
                    .companyId(req.getCompanyId())
                    .companyResourceId(req.getCompanyResourceId())
                    .parentResourceGraphId(req.getParentResourceGraphId())
                    .resourceUrl(trimmed)
                    .resourceType(LINK_RESOURCE_TYPE)
                    .parentResourceType(SEED_RESOURCE_TYPE)
                    .crawlStatus(CrawlStatus.DISCOVERED.name())
                    .status(Status.DEFAULT)
                    .createdDt(now).updatedDt(now)
                    .createdBy("airflow").updatedBy("airflow")
                    .build());
            added++;
        }
        // mark the root with the final crawl status reported by the DAG
        if (req.getParentResourceGraphId() != null) {
            graphRepository.findById(req.getParentResourceGraphId()).ifPresent(root -> {
                root.setCrawlStatus(req.getStatus() != null ? req.getStatus() : CrawlStatus.DISCOVERED.name());
                root.setUpdatedDt(Instant.now());
                graphRepository.save(root);
            });
        }
        log.info("Recorded {} discovered link(s) under graph root {}", added, req.getParentResourceGraphId());
        ctx.setRespDTO(new RecordDiscoveredRespDTO(added, req.getParentResourceGraphId()));
    }

    @Transactional(readOnly = true)
    public void getGraph(GetGraphCtx ctx) {
        String companyId = ctx.getReqDTO().getCompanyId();
        List<ResourceGraphNodeDTO> nodes = graphRepository.findByCompanyId(companyId).stream()
                .map(ResourceGraphNodeMapper::toDTO)
                .toList();
        ctx.setRespDTO(new GetGraphRespDTO(nodes, nodes.size()));
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
}
