package com.jk.labs.vkp.company.api.controller;

import com.jk.labs.vkp.company.common.dto.company.CreateCompCtx;
import com.jk.labs.vkp.company.common.dto.company.CreateCompReqDTO;
import com.jk.labs.vkp.company.common.dto.company.CreateCompRespDTO;
import com.jk.labs.vkp.company.common.dto.company.CompDTO;
import com.jk.labs.vkp.company.common.dto.company.DeleteCompCtx;
import com.jk.labs.vkp.company.common.dto.company.DeleteCompReqDTO;
import com.jk.labs.vkp.company.common.dto.company.DeleteCompRespDTO;
import com.jk.labs.vkp.company.common.dto.company.GetCompCtx;
import com.jk.labs.vkp.company.common.dto.company.GetCompReqDTO;
import com.jk.labs.vkp.company.common.dto.company.GetCompRespDTO;
import com.jk.labs.vkp.company.common.dto.company.ListCompsCtx;
import com.jk.labs.vkp.company.common.dto.company.ListCompsReqDTO;
import com.jk.labs.vkp.company.common.dto.company.ListCompsRespDTO;
import com.jk.labs.vkp.company.common.dto.company.UpdateCompCtx;
import com.jk.labs.vkp.company.common.dto.company.UpdateCompReqDTO;
import com.jk.labs.vkp.company.common.dto.company.UpdateCompRespDTO;
import com.jk.labs.vkp.company.common.api.ApiRoutes;
import com.jk.labs.vkp.company.service.CompService;
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
 * Admin-facing Company CRUD API.
 *
 * Controllers adapt HTTP to the use case {@code Ctx}: build the Ctx, set its ReqDTO,
 * delegate to the service, and return the RespDTO the service wrote back.
 */
@RestController
@RequestMapping(ApiRoutes.COMPANIES)
@RequiredArgsConstructor
public class CompController {

    private final CompService companyService;

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public CreateCompRespDTO create(@Valid @RequestBody CompDTO company) {
        CreateCompCtx ctx = new CreateCompCtx();
        ctx.setReqDTO(new CreateCompReqDTO(company));
        companyService.create(ctx);
        return ctx.getRespDTO();
    }

    @GetMapping
    public ListCompsRespDTO list(@RequestParam(required = false) String status) {
        ListCompsCtx ctx = new ListCompsCtx();
        ctx.setReqDTO(new ListCompsReqDTO(status));
        companyService.list(ctx);
        return ctx.getRespDTO();
    }

    @GetMapping("/{companyId}")
    public GetCompRespDTO get(@PathVariable String companyId) {
        GetCompCtx ctx = new GetCompCtx();
        ctx.setReqDTO(new GetCompReqDTO(companyId));
        companyService.get(ctx);
        return ctx.getRespDTO();
    }

    @PutMapping("/{companyId}")
    public UpdateCompRespDTO update(@PathVariable String companyId,
                                        @Valid @RequestBody CompDTO company) {
        UpdateCompCtx ctx = new UpdateCompCtx();
        ctx.setReqDTO(new UpdateCompReqDTO(companyId, company));
        companyService.update(ctx);
        return ctx.getRespDTO();
    }

    @DeleteMapping("/{companyId}")
    public DeleteCompRespDTO delete(@PathVariable String companyId) {
        DeleteCompCtx ctx = new DeleteCompCtx();
        ctx.setReqDTO(new DeleteCompReqDTO(companyId));
        companyService.delete(ctx);
        return ctx.getRespDTO();
    }
}
