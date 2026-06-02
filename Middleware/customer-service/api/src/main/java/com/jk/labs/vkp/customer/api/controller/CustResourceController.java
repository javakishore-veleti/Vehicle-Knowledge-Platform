package com.jk.labs.vkp.customer.api.controller;

import com.jk.labs.vkp.customer.common.dto.resource.CreateCustResourceCtx;
import com.jk.labs.vkp.customer.common.dto.resource.CreateCustResourceReqDTO;
import com.jk.labs.vkp.customer.common.dto.resource.CreateCustResourceRespDTO;
import com.jk.labs.vkp.customer.common.dto.resource.CustResourceDTO;
import com.jk.labs.vkp.customer.common.dto.resource.DeleteCustResourceCtx;
import com.jk.labs.vkp.customer.common.dto.resource.DeleteCustResourceReqDTO;
import com.jk.labs.vkp.customer.common.dto.resource.DeleteCustResourceRespDTO;
import com.jk.labs.vkp.customer.common.dto.resource.ListCustResourcesCtx;
import com.jk.labs.vkp.customer.common.dto.resource.ListCustResourcesReqDTO;
import com.jk.labs.vkp.customer.common.dto.resource.ListCustResourcesRespDTO;
import com.jk.labs.vkp.customer.common.dto.resource.UpdateCustResourceCtx;
import com.jk.labs.vkp.customer.common.dto.resource.UpdateCustResourceReqDTO;
import com.jk.labs.vkp.customer.common.dto.resource.UpdateCustResourceRespDTO;
import com.jk.labs.vkp.customer.common.api.ApiRoutes;
import com.jk.labs.vkp.customer.service.CustResourceService;
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
 * Admin-facing Customer Resource CRUD API (resources nested under a customer).
 */
@RestController
@RequestMapping(ApiRoutes.CUSTOMER_RESOURCES)
@RequiredArgsConstructor
public class CustResourceController {

    private final CustResourceService resourceService;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public CreateCustResourceRespDTO create(@PathVariable String customerId,
                                                @Valid @RequestBody CustResourceDTO resource) {
        CreateCustResourceCtx ctx = new CreateCustResourceCtx();
        ctx.setReqDTO(new CreateCustResourceReqDTO(customerId, resource));
        resourceService.create(ctx);
        return ctx.getRespDTO();
    }

    @GetMapping
    public ListCustResourcesRespDTO list(@PathVariable String customerId) {
        ListCustResourcesCtx ctx = new ListCustResourcesCtx();
        ctx.setReqDTO(new ListCustResourcesReqDTO(customerId));
        resourceService.list(ctx);
        return ctx.getRespDTO();
    }

    @PutMapping("/{resourceId}")
    public UpdateCustResourceRespDTO update(@PathVariable String customerId,
                                                @PathVariable String resourceId,
                                                @Valid @RequestBody CustResourceDTO resource) {
        UpdateCustResourceCtx ctx = new UpdateCustResourceCtx();
        ctx.setReqDTO(new UpdateCustResourceReqDTO(customerId, resourceId, resource));
        resourceService.update(ctx);
        return ctx.getRespDTO();
    }

    @DeleteMapping("/{resourceId}")
    public DeleteCustResourceRespDTO delete(@PathVariable String customerId,
                                                @PathVariable String resourceId) {
        DeleteCustResourceCtx ctx = new DeleteCustResourceCtx();
        ctx.setReqDTO(new DeleteCustResourceReqDTO(customerId, resourceId));
        resourceService.delete(ctx);
        return ctx.getRespDTO();
    }
}
