package com.jk.labs.vkp.customer.api.controller;

import com.jk.labs.vkp.customer.common.dto.customer.CreateCustCtx;
import com.jk.labs.vkp.customer.common.dto.customer.CreateCustReqDTO;
import com.jk.labs.vkp.customer.common.dto.customer.CreateCustRespDTO;
import com.jk.labs.vkp.customer.common.dto.customer.CustDTO;
import com.jk.labs.vkp.customer.common.dto.customer.DeleteCustCtx;
import com.jk.labs.vkp.customer.common.dto.customer.DeleteCustReqDTO;
import com.jk.labs.vkp.customer.common.dto.customer.DeleteCustRespDTO;
import com.jk.labs.vkp.customer.common.dto.customer.GetCustCtx;
import com.jk.labs.vkp.customer.common.dto.customer.GetCustReqDTO;
import com.jk.labs.vkp.customer.common.dto.customer.GetCustRespDTO;
import com.jk.labs.vkp.customer.common.dto.customer.ListCustsCtx;
import com.jk.labs.vkp.customer.common.dto.customer.ListCustsReqDTO;
import com.jk.labs.vkp.customer.common.dto.customer.ListCustsRespDTO;
import com.jk.labs.vkp.customer.common.dto.customer.UpdateCustCtx;
import com.jk.labs.vkp.customer.common.dto.customer.UpdateCustReqDTO;
import com.jk.labs.vkp.customer.common.dto.customer.UpdateCustRespDTO;
import com.jk.labs.vkp.customer.common.api.ApiRoutes;
import com.jk.labs.vkp.customer.service.CustService;
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
 * Admin-facing Customer CRUD API.
 *
 * Controllers adapt HTTP to the use case {@code Ctx}: build the Ctx, set its ReqDTO,
 * delegate to the service, and return the RespDTO the service wrote back.
 */
@RestController
@RequestMapping(ApiRoutes.CUSTOMERS)
@RequiredArgsConstructor
public class CustController {

    private final CustService customerService;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public CreateCustRespDTO create(@Valid @RequestBody CustDTO customer) {
        CreateCustCtx ctx = new CreateCustCtx();
        ctx.setReqDTO(new CreateCustReqDTO(customer));
        customerService.create(ctx);
        return ctx.getRespDTO();
    }

    @GetMapping
    public ListCustsRespDTO list(@RequestParam(required = false) String status) {
        ListCustsCtx ctx = new ListCustsCtx();
        ctx.setReqDTO(new ListCustsReqDTO(status));
        customerService.list(ctx);
        return ctx.getRespDTO();
    }

    @GetMapping("/{customerId}")
    public GetCustRespDTO get(@PathVariable String customerId) {
        GetCustCtx ctx = new GetCustCtx();
        ctx.setReqDTO(new GetCustReqDTO(customerId));
        customerService.get(ctx);
        return ctx.getRespDTO();
    }

    @PutMapping("/{customerId}")
    public UpdateCustRespDTO update(@PathVariable String customerId,
                                        @Valid @RequestBody CustDTO customer) {
        UpdateCustCtx ctx = new UpdateCustCtx();
        ctx.setReqDTO(new UpdateCustReqDTO(customerId, customer));
        customerService.update(ctx);
        return ctx.getRespDTO();
    }

    @DeleteMapping("/{customerId}")
    public DeleteCustRespDTO delete(@PathVariable String customerId) {
        DeleteCustCtx ctx = new DeleteCustCtx();
        ctx.setReqDTO(new DeleteCustReqDTO(customerId));
        customerService.delete(ctx);
        return ctx.getRespDTO();
    }
}
