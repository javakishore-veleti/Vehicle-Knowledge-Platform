package com.jk.labs.vkp.cef.admin.service;

import com.jk.labs.vkp.cef.admin.dto.StrategyDTO;
import com.jk.labs.vkp.cef.admin.entity.CefStrategyEntity;
import com.jk.labs.vkp.cef.admin.repository.CefStrategyRepository;
import lombok.RequiredArgsConstructor;
import org.springframework.http.HttpStatus;
import org.springframework.stereotype.Service;
import org.springframework.web.server.ResponseStatusException;

import java.time.Instant;
import java.util.List;
import java.util.UUID;

@Service
@RequiredArgsConstructor
public class StrategyService {

    private final CefStrategyRepository repo;

    public List<StrategyDTO> list() {
        return repo.findAll().stream().map(StrategyService::toDto).toList();
    }

    public StrategyDTO get(String id) {
        return toDto(find(id));
    }

    public StrategyDTO create(StrategyDTO req) {
        CefStrategyEntity e = new CefStrategyEntity();
        e.setId(UUID.randomUUID().toString());
        e.setCreatedDt(Instant.now());
        apply(e, req);
        return toDto(repo.save(e));
    }

    public StrategyDTO update(String id, StrategyDTO req) {
        CefStrategyEntity e = find(id);
        apply(e, req);
        return toDto(repo.save(e));
    }

    public void delete(String id) {
        repo.delete(find(id));
    }

    private CefStrategyEntity find(String id) {
        return repo.findById(id).orElseThrow(
                () -> new ResponseStatusException(HttpStatus.NOT_FOUND, "strategy not found: " + id));
    }

    private void apply(CefStrategyEntity e, StrategyDTO d) {
        e.setName(d.getName());
        e.setDescription(d.getDescription());
        e.setSelectionEnabled(d.isSelectionEnabled());
        e.setCompressionEnabled(d.isCompressionEnabled());
        e.setOrderingEnabled(d.isOrderingEnabled());
        e.setIsolationEnabled(d.isIsolationEnabled());
        e.setFormatEnabled(d.isFormatEnabled());
        e.setCharBudget(d.getCharBudget());
        e.setStatus(d.getStatus() == null ? "ACTIVE" : d.getStatus());
        e.setUpdatedDt(Instant.now());
    }

    private static StrategyDTO toDto(CefStrategyEntity e) {
        StrategyDTO d = new StrategyDTO();
        d.setId(e.getId());
        d.setName(e.getName());
        d.setDescription(e.getDescription());
        d.setSelectionEnabled(e.isSelectionEnabled());
        d.setCompressionEnabled(e.isCompressionEnabled());
        d.setOrderingEnabled(e.isOrderingEnabled());
        d.setIsolationEnabled(e.isIsolationEnabled());
        d.setFormatEnabled(e.isFormatEnabled());
        d.setCharBudget(e.getCharBudget());
        d.setStatus(e.getStatus());
        return d;
    }
}
