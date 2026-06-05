package com.jk.labs.vkp.cef.admin.api;

import com.jk.labs.vkp.cef.admin.dto.StrategyDTO;
import com.jk.labs.vkp.cef.admin.service.StrategyService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

import java.util.List;

/** CEF context-strategy CRUD. Versioned admin route per VKP convention. */
@RestController
@RequestMapping("/admin/context-engine/service/v1/crud/strategies")
@RequiredArgsConstructor
public class StrategyController {

    private final StrategyService service;

    @GetMapping
    public List<StrategyDTO> list() {
        return service.list();
    }

    @GetMapping("/{id}")
    public StrategyDTO get(@PathVariable String id) {
        return service.get(id);
    }

    @PostMapping
    @ResponseStatus(HttpStatus.CREATED)
    public StrategyDTO create(@Valid @RequestBody StrategyDTO req) {
        return service.create(req);
    }

    @PutMapping("/{id}")
    public StrategyDTO update(@PathVariable String id, @Valid @RequestBody StrategyDTO req) {
        return service.update(id, req);
    }

    @DeleteMapping("/{id}")
    @ResponseStatus(HttpStatus.NO_CONTENT)
    public void delete(@PathVariable String id) {
        service.delete(id);
    }
}
