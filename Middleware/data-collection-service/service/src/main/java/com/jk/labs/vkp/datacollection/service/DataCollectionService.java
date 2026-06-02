package com.jk.labs.vkp.datacollection.service;

import com.jk.labs.vkp.datacollection.common.dto.discover.DiscoverCtx;
import com.jk.labs.vkp.datacollection.common.dto.discover.DiscoverReqDTO;
import com.jk.labs.vkp.datacollection.common.dto.discover.DiscoverRespDTO;
import com.jk.labs.vkp.datacollection.common.dto.graph.GetGraphCtx;
import com.jk.labs.vkp.datacollection.common.dto.graph.GetGraphRespDTO;
import com.jk.labs.vkp.datacollection.common.dto.graph.ResourceGraphNodeDTO;
import com.jk.labs.vkp.datacollection.common.dto.status.GetStatusCtx;
import com.jk.labs.vkp.datacollection.common.dto.status.GetStatusReqDTO;
import com.jk.labs.vkp.datacollection.common.dto.status.GetStatusRespDTO;
import com.jk.labs.vkp.datacollection.common.enums.CrawlStatus;
import com.jk.labs.vkp.datacollection.common.enums.Status;
import com.jk.labs.vkp.datacollection.dao.entity.ResourceGraphNodeEntity;
import com.jk.labs.vkp.datacollection.dao.repository.ResourceGraphNodeRepository;
import com.jk.labs.vkp.datacollection.service.mapper.ResourceGraphNodeMapper;
import com.jk.labs.vkp.datacollection.utils.AuditUtils;
import com.jk.labs.vkp.datacollection.utils.IdGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
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

    private final ResourceGraphNodeRepository graphRepository;
    private final AirflowAdapterClient adapterClient;

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
        AirflowAdapterClient.DagRunRef run = adapterClient.triggerDag(DISCOVER_DAG_ID, conf, actor);

        log.info("Discovery triggered: company={} resource={} -> dagRun={} (graphRoot={})",
                req.getCompanyId(), req.getCompanyResourceId(), run.dagRunId(), rootId);
        ctx.setRespDTO(new DiscoverRespDTO(rootId,
                run.dagId() != null ? run.dagId() : DISCOVER_DAG_ID, run.dagRunId(), run.state()));
    }

    @Transactional(readOnly = true)
    public void getGraph(GetGraphCtx ctx) {
        String companyId = ctx.getReqDTO().getCompanyId();
        List<ResourceGraphNodeDTO> nodes = graphRepository.findByCompanyId(companyId).stream()
                .map(ResourceGraphNodeMapper::toDTO)
                .toList();
        ctx.setRespDTO(new GetGraphRespDTO(nodes, nodes.size()));
    }

    public void getStatus(GetStatusCtx ctx) {
        GetStatusReqDTO req = ctx.getReqDTO();
        AirflowAdapterClient.DagRunRef run = adapterClient.getRun(req.getDagId(), req.getRunId());
        ctx.setRespDTO(new GetStatusRespDTO(run.dagId() != null ? run.dagId() : req.getDagId(),
                run.dagRunId(), run.state()));
    }
}
