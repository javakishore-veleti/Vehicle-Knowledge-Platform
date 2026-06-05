package com.jk.labs.vkp.cef.admin;

import com.jk.labs.vkp.cef.admin.dto.StrategyDTO;
import com.jk.labs.vkp.cef.admin.entity.CefStrategyEntity;
import com.jk.labs.vkp.cef.admin.repository.CefStrategyRepository;
import com.jk.labs.vkp.cef.admin.service.StrategyService;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.web.server.ResponseStatusException;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class StrategyServiceTest {

    @Mock
    CefStrategyRepository repo;
    @InjectMocks
    StrategyService service;

    @Test
    void createAssignsIdTimestampsAndMapsFields() {
        when(repo.save(any(CefStrategyEntity.class))).thenAnswer(inv -> inv.getArgument(0));
        StrategyDTO req = new StrategyDTO();
        req.setName("lean");
        req.setCompressionEnabled(false);
        req.setCharBudget(3000);

        StrategyDTO out = service.create(req);

        assertNotNull(out.getId());
        assertEquals("lean", out.getName());
        assertFalse(out.isCompressionEnabled());
        assertEquals(3000, out.getCharBudget());
        assertEquals("ACTIVE", out.getStatus());
    }

    @Test
    void getMissingThrows404() {
        when(repo.findById("nope")).thenReturn(Optional.empty());
        ResponseStatusException ex = assertThrows(ResponseStatusException.class, () -> service.get("nope"));
        assertEquals(404, ex.getStatusCode().value());
    }

    @Test
    void updateAppliesFields() {
        CefStrategyEntity e = new CefStrategyEntity();
        e.setId("s1");
        e.setName("old");
        when(repo.findById("s1")).thenReturn(Optional.of(e));
        when(repo.save(any(CefStrategyEntity.class))).thenAnswer(inv -> inv.getArgument(0));

        StrategyDTO req = new StrategyDTO();
        req.setName("new");
        req.setIsolationEnabled(true);
        StrategyDTO out = service.update("s1", req);

        assertEquals("new", out.getName());
        assertTrue(out.isIsolationEnabled());
    }
}
