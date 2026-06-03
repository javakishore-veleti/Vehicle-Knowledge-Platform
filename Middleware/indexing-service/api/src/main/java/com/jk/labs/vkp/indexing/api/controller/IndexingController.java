package com.jk.labs.vkp.indexing.api.controller;

import com.jk.labs.vkp.indexing.common.api.ApiRoutes;
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
import com.jk.labs.vkp.indexing.service.IndexingService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

import java.util.List;

/** Indexing control-plane API: registry listings, trigger, logs, executor callback. */
@RestController
@RequiredArgsConstructor
public class IndexingController {

    private final IndexingService indexingService;

    @GetMapping(ApiRoutes.WORKFLOWS)
    public List<WorkflowDTO> workflows() {
        return indexingService.listWorkflows();
    }

    @GetMapping(ApiRoutes.FORMULAS)
    public List<FormulaDTO> formulas() {
        return indexingService.listFormulas();
    }

    @GetMapping(ApiRoutes.CREDENTIALS)
    public List<CredentialDTO> credentials() {
        return indexingService.listCredentials();
    }

    @GetMapping(ApiRoutes.LOGS)
    public List<IndexLogDTO> logs(@PathVariable String companyId) {
        return indexingService.listLogs(companyId);
    }

    @PostMapping(ApiRoutes.TRIGGER)
    @ResponseStatus(HttpStatus.ACCEPTED)
    public TriggerIndexRespDTO trigger(@PathVariable String companyId,
                                       @Valid @RequestBody TriggerIndexReqDTO req) {
        req.setCompanyId(companyId);
        TriggerIndexCtx ctx = new TriggerIndexCtx();
        ctx.setReqDTO(req);
        indexingService.trigger(ctx);
        return ctx.getRespDTO();
    }

    @PostMapping(ApiRoutes.CALLBACK)
    public IndexCallbackRespDTO callback(@PathVariable String indexLogId,
                                         @Valid @RequestBody IndexCallbackReqDTO req) {
        req.setIndexLogId(indexLogId);
        IndexCallbackCtx ctx = new IndexCallbackCtx();
        ctx.setReqDTO(req);
        indexingService.callback(ctx);
        return ctx.getRespDTO();
    }
}
