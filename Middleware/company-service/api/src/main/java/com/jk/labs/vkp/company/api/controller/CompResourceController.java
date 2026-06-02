package com.jk.labs.vkp.company.api.controller;

import com.jk.labs.vkp.company.common.dto.resource.CreateCompResourceCtx;
import com.jk.labs.vkp.company.common.dto.resource.CreateCompResourceReqDTO;
import com.jk.labs.vkp.company.common.dto.resource.CreateCompResourceRespDTO;
import com.jk.labs.vkp.company.common.dto.resource.CompResourceDTO;
import com.jk.labs.vkp.company.common.dto.resource.DeleteCompResourceCtx;
import com.jk.labs.vkp.company.common.dto.resource.DeleteCompResourceReqDTO;
import com.jk.labs.vkp.company.common.dto.resource.DeleteCompResourceRespDTO;
import com.jk.labs.vkp.company.common.dto.resource.ListCompResourcesCtx;
import com.jk.labs.vkp.company.common.dto.resource.ListCompResourcesReqDTO;
import com.jk.labs.vkp.company.common.dto.resource.ListCompResourcesRespDTO;
import com.jk.labs.vkp.company.common.dto.resource.UpdateCompResourceCtx;
import com.jk.labs.vkp.company.common.dto.resource.UpdateCompResourceReqDTO;
import com.jk.labs.vkp.company.common.dto.resource.UpdateCompResourceRespDTO;
import com.jk.labs.vkp.company.common.api.ApiRoutes;
import com.jk.labs.vkp.company.service.CompResourceService;
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
import org.springframework.web.bind.annotation.ResponseStatus;
import org.springframework.web.bind.annotation.RestController;

/**
 * Admin-facing Company Resource CRUD API (resources nested under a company).
 */
@RestController
@RequestMapping(ApiRoutes.COMPANY_RESOURCES)
@RequiredArgsConstructor
public class CompResourceController {

    private final CompResourceService resourceService;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public CreateCompResourceRespDTO create(@PathVariable String companyId,
                                                @Valid @RequestBody CompResourceDTO resource) {
        CreateCompResourceCtx ctx = new CreateCompResourceCtx();
        ctx.setReqDTO(new CreateCompResourceReqDTO(companyId, resource));
        resourceService.create(ctx);
        return ctx.getRespDTO();
    }

    @GetMapping
    public ListCompResourcesRespDTO list(@PathVariable String companyId) {
        ListCompResourcesCtx ctx = new ListCompResourcesCtx();
        ctx.setReqDTO(new ListCompResourcesReqDTO(companyId));
        resourceService.list(ctx);
        return ctx.getRespDTO();
    }

    @PutMapping("/{resourceId}")
    public UpdateCompResourceRespDTO update(@PathVariable String companyId,
                                                @PathVariable String resourceId,
                                                @Valid @RequestBody CompResourceDTO resource) {
        UpdateCompResourceCtx ctx = new UpdateCompResourceCtx();
        ctx.setReqDTO(new UpdateCompResourceReqDTO(companyId, resourceId, resource));
        resourceService.update(ctx);
        return ctx.getRespDTO();
    }

    @DeleteMapping("/{resourceId}")
    public DeleteCompResourceRespDTO delete(@PathVariable String companyId,
                                                @PathVariable String resourceId) {
        DeleteCompResourceCtx ctx = new DeleteCompResourceCtx();
        ctx.setReqDTO(new DeleteCompResourceReqDTO(companyId, resourceId));
        resourceService.delete(ctx);
        return ctx.getRespDTO();
    }
}
