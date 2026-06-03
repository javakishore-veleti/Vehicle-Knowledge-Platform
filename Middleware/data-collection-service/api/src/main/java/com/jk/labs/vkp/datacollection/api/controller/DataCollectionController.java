package com.jk.labs.vkp.datacollection.api.controller;

import com.jk.labs.vkp.datacollection.common.api.ApiRoutes;
import com.jk.labs.vkp.datacollection.common.dto.crawl.TriggerCrawlCtx;
import com.jk.labs.vkp.datacollection.common.dto.crawl.TriggerCrawlReqDTO;
import com.jk.labs.vkp.datacollection.common.dto.crawl.TriggerCrawlRespDTO;
import com.jk.labs.vkp.datacollection.common.dto.discover.DiscoverCtx;
import com.jk.labs.vkp.datacollection.common.dto.discover.DiscoverReqDTO;
import com.jk.labs.vkp.datacollection.common.dto.discover.DiscoverRespDTO;
import com.jk.labs.vkp.datacollection.common.dto.discover.RecordDiscoveredCtx;
import com.jk.labs.vkp.datacollection.common.dto.discover.RecordDiscoveredReqDTO;
import com.jk.labs.vkp.datacollection.common.dto.discover.RecordDiscoveredRespDTO;
import com.jk.labs.vkp.datacollection.common.dto.graph.GetGraphCtx;
import com.jk.labs.vkp.datacollection.common.dto.graph.GetGraphReqDTO;
import com.jk.labs.vkp.datacollection.common.dto.graph.GetGraphRespDTO;
import com.jk.labs.vkp.datacollection.common.dto.status.GetStatusCtx;
import com.jk.labs.vkp.datacollection.common.dto.status.GetStatusReqDTO;
import com.jk.labs.vkp.datacollection.common.dto.status.GetStatusRespDTO;
import com.jk.labs.vkp.datacollection.common.dto.workflow.ListWorkflowsCtx;
import com.jk.labs.vkp.datacollection.common.dto.workflow.ListWorkflowsReqDTO;
import com.jk.labs.vkp.datacollection.common.dto.workflow.ListWorkflowsRespDTO;
import com.jk.labs.vkp.datacollection.service.DataCollectionService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

/**
 * Admin-facing data-collection API. Triggers link discovery and reads the resource graph;
 * never touches Airflow directly (goes through airflow-adapter-service).
 */
@RestController
@RequiredArgsConstructor
public class DataCollectionController {

    private final DataCollectionService dataCollectionService;

    @PostMapping(ApiRoutes.DISCOVER)
    @ResponseStatus(HttpStatus.ACCEPTED)
    public DiscoverRespDTO discover(@PathVariable String companyId,
                                    @PathVariable String resourceId,
                                    @Valid @RequestBody DiscoverReqDTO req) {
        req.setCompanyId(companyId);
        req.setCompanyResourceId(resourceId);
        DiscoverCtx ctx = new DiscoverCtx();
        ctx.setReqDTO(req);
        dataCollectionService.discover(ctx);
        return ctx.getRespDTO();
    }

    @PostMapping(ApiRoutes.CRAWL)
    @ResponseStatus(HttpStatus.ACCEPTED)
    public TriggerCrawlRespDTO crawl(@PathVariable String companyId,
                                     @RequestBody(required = false) TriggerCrawlReqDTO body) {
        TriggerCrawlReqDTO req = body != null ? body : new TriggerCrawlReqDTO();
        req.setCompanyId(companyId);
        TriggerCrawlCtx ctx = new TriggerCrawlCtx();
        ctx.setReqDTO(req);
        dataCollectionService.triggerCrawl(ctx);
        return ctx.getRespDTO();
    }

    @PostMapping(ApiRoutes.GRAPH_RECORD)
    public RecordDiscoveredRespDTO recordDiscovered(@Valid @RequestBody RecordDiscoveredReqDTO req) {
        RecordDiscoveredCtx ctx = new RecordDiscoveredCtx();
        ctx.setReqDTO(req);
        dataCollectionService.recordDiscovered(ctx);
        return ctx.getRespDTO();
    }

    @GetMapping(ApiRoutes.RESOURCE_GRAPH)
    public GetGraphRespDTO resourceGraph(@PathVariable String companyId) {
        GetGraphCtx ctx = new GetGraphCtx();
        ctx.setReqDTO(new GetGraphReqDTO(companyId));
        dataCollectionService.getGraph(ctx);
        return ctx.getRespDTO();
    }

    @GetMapping(ApiRoutes.WORKFLOWS)
    public ListWorkflowsRespDTO workflows(@PathVariable String dagId) {
        ListWorkflowsCtx ctx = new ListWorkflowsCtx();
        ctx.setReqDTO(new ListWorkflowsReqDTO(dagId));
        dataCollectionService.listWorkflows(ctx);
        return ctx.getRespDTO();
    }

    @GetMapping(ApiRoutes.RUN_STATUS)
    public GetStatusRespDTO runStatus(@PathVariable String dagId, @PathVariable String runId) {
        GetStatusCtx ctx = new GetStatusCtx();
        ctx.setReqDTO(new GetStatusReqDTO(dagId, runId));
        dataCollectionService.getStatus(ctx);
        return ctx.getRespDTO();
    }
}
