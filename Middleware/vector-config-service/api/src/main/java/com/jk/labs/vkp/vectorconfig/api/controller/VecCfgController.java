package com.jk.labs.vkp.vectorconfig.api.controller;

import com.jk.labs.vkp.vectorconfig.common.api.ApiRoutes;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.CreateVecCfgCtx;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.CreateVecCfgReqDTO;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.CreateVecCfgRespDTO;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.DeleteVecCfgCtx;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.DeleteVecCfgReqDTO;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.DeleteVecCfgRespDTO;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.GetVecCfgCtx;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.GetVecCfgReqDTO;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.GetVecCfgRespDTO;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.ListVecCfgsCtx;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.ListVecCfgsReqDTO;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.ListVecCfgsRespDTO;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.UpdateVecCfgCtx;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.UpdateVecCfgReqDTO;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.UpdateVecCfgRespDTO;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.VecCfgDTO;
import com.jk.labs.vkp.vectorconfig.service.VecCfgService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.DeleteMapping;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.PutMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

/**
 * Admin-facing Vector Config CRUD API. Determines where each company resource's content is
 * indexed (one or many stores; at most one primary). Controllers adapt HTTP to the use case
 * {@code Ctx}: build the Ctx, set its ReqDTO, delegate, return the RespDTO.
 */
@RestController
@RequestMapping(ApiRoutes.CRUD)
@RequiredArgsConstructor
public class VecCfgController {

    private final VecCfgService vectorConfigService;

    /** POST /admin/vector-config/service/v1/crud/company-resources/{companyResourceId}/vector-configs */
    @PostMapping("/company-resources/{companyResourceId}/vector-configs")
    @ResponseStatus(HttpStatus.CREATED)
    public CreateVecCfgRespDTO create(@PathVariable String companyResourceId,
                                      @Valid @RequestBody VecCfgDTO vectorConfig) {
        CreateVecCfgCtx ctx = new CreateVecCfgCtx();
        ctx.setReqDTO(new CreateVecCfgReqDTO(companyResourceId, vectorConfig));
        vectorConfigService.create(ctx);
        return ctx.getRespDTO();
    }

    /** GET .../crud/company-resources/{companyResourceId}/vector-configs */
    @GetMapping("/company-resources/{companyResourceId}/vector-configs")
    public ListVecCfgsRespDTO listForResource(@PathVariable String companyResourceId) {
        ListVecCfgsCtx ctx = new ListVecCfgsCtx();
        ctx.setReqDTO(new ListVecCfgsReqDTO(companyResourceId, null, null));
        vectorConfigService.list(ctx);
        return ctx.getRespDTO();
    }

    /** GET .../crud/vector-configs?companyId=&status= */
    @GetMapping("/vector-configs")
    public ListVecCfgsRespDTO list(@RequestParam(required = false) String companyId,
                                   @RequestParam(required = false) String status) {
        ListVecCfgsCtx ctx = new ListVecCfgsCtx();
        ctx.setReqDTO(new ListVecCfgsReqDTO(null, companyId, status));
        vectorConfigService.list(ctx);
        return ctx.getRespDTO();
    }

    /** GET .../crud/vector-configs/{vectorConfigId} */
    @GetMapping("/vector-configs/{vectorConfigId}")
    public GetVecCfgRespDTO get(@PathVariable String vectorConfigId) {
        GetVecCfgCtx ctx = new GetVecCfgCtx();
        ctx.setReqDTO(new GetVecCfgReqDTO(vectorConfigId));
        vectorConfigService.get(ctx);
        return ctx.getRespDTO();
    }

    /** PUT .../crud/vector-configs/{vectorConfigId} */
    @PutMapping("/vector-configs/{vectorConfigId}")
    public UpdateVecCfgRespDTO update(@PathVariable String vectorConfigId,
                                      @Valid @RequestBody VecCfgDTO vectorConfig) {
        UpdateVecCfgCtx ctx = new UpdateVecCfgCtx();
        ctx.setReqDTO(new UpdateVecCfgReqDTO(vectorConfigId, vectorConfig));
        vectorConfigService.update(ctx);
        return ctx.getRespDTO();
    }

    /** DELETE .../crud/vector-configs/{vectorConfigId} */
    @DeleteMapping("/vector-configs/{vectorConfigId}")
    public DeleteVecCfgRespDTO delete(@PathVariable String vectorConfigId) {
        DeleteVecCfgCtx ctx = new DeleteVecCfgCtx();
        ctx.setReqDTO(new DeleteVecCfgReqDTO(vectorConfigId));
        vectorConfigService.delete(ctx);
        return ctx.getRespDTO();
    }
}
