package com.jk.labs.vkp.ingestion.api.controller;

import com.jk.labs.vkp.ingestion.common.api.ApiRoutes;
import com.jk.labs.vkp.ingestion.common.dto.content.ContentRecordCtx;
import com.jk.labs.vkp.ingestion.common.dto.content.ContentRecordReqDTO;
import com.jk.labs.vkp.ingestion.common.dto.content.ContentRecordRespDTO;
import com.jk.labs.vkp.ingestion.common.dto.content.ListContentCtx;
import com.jk.labs.vkp.ingestion.common.dto.content.ListContentReqDTO;
import com.jk.labs.vkp.ingestion.common.dto.content.ListContentRespDTO;
import com.jk.labs.vkp.ingestion.common.dto.ingest.IngestCtx;
import com.jk.labs.vkp.ingestion.common.dto.ingest.IngestReqDTO;
import com.jk.labs.vkp.ingestion.common.dto.ingest.IngestRespDTO;
import com.jk.labs.vkp.ingestion.common.dto.status.GetStatusCtx;
import com.jk.labs.vkp.ingestion.common.dto.status.GetStatusReqDTO;
import com.jk.labs.vkp.ingestion.common.dto.status.GetStatusRespDTO;
import com.jk.labs.vkp.ingestion.common.dto.workflow.ListWorkflowsCtx;
import com.jk.labs.vkp.ingestion.common.dto.workflow.ListWorkflowsReqDTO;
import com.jk.labs.vkp.ingestion.common.dto.workflow.ListWorkflowsRespDTO;
import com.jk.labs.vkp.ingestion.service.IngestionService;
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
 * Admin-facing ingestion API. Triggers content extraction and reads stored content;
 * never touches Airflow directly (goes through airflow-adapter-service).
 */
@RestController
@RequiredArgsConstructor
public class IngestionController {

    private final IngestionService ingestionService;

    @PostMapping(ApiRoutes.INGEST)
    @ResponseStatus(HttpStatus.ACCEPTED)
    public IngestRespDTO ingest(@PathVariable String companyId,
                                @PathVariable String resourceId,
                                @RequestBody(required = false) IngestReqDTO body) {
        IngestReqDTO req = body != null ? body : new IngestReqDTO();
        req.setCompanyId(companyId);
        req.setCompanyResourceId(resourceId);
        IngestCtx ctx = new IngestCtx();
        ctx.setReqDTO(req);
        ingestionService.ingest(ctx);
        return ctx.getRespDTO();
    }

    @PostMapping(ApiRoutes.CONTENT_RECORD)
    public ContentRecordRespDTO recordContent(@Valid @RequestBody ContentRecordReqDTO req) {
        ContentRecordCtx ctx = new ContentRecordCtx();
        ctx.setReqDTO(req);
        ingestionService.recordContent(ctx);
        return ctx.getRespDTO();
    }

    @GetMapping(ApiRoutes.CONTENT)
    public ListContentRespDTO content(@PathVariable String companyId) {
        ListContentCtx ctx = new ListContentCtx();
        ctx.setReqDTO(new ListContentReqDTO(companyId));
        ingestionService.listContent(ctx);
        return ctx.getRespDTO();
    }

    @GetMapping(ApiRoutes.WORKFLOWS)
    public ListWorkflowsRespDTO workflows(@PathVariable String dagId) {
        ListWorkflowsCtx ctx = new ListWorkflowsCtx();
        ctx.setReqDTO(new ListWorkflowsReqDTO(dagId));
        ingestionService.listWorkflows(ctx);
        return ctx.getRespDTO();
    }

    @GetMapping(ApiRoutes.RUN_STATUS)
    public GetStatusRespDTO runStatus(@PathVariable String dagId, @PathVariable String runId) {
        GetStatusCtx ctx = new GetStatusCtx();
        ctx.setReqDTO(new GetStatusReqDTO(dagId, runId));
        ingestionService.getStatus(ctx);
        return ctx.getRespDTO();
    }
}
