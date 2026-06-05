package com.jk.labs.vkp.cef.admin.config;

import com.jk.labs.vkp.cef.admin.dto.StrategyDTO;
import com.jk.labs.vkp.cef.admin.service.StrategyService;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;

/** Seeds two default context strategies on first boot. */
@Component
@Slf4j
@RequiredArgsConstructor
public class StrategySeeder {

    private final StrategyService service;

    @EventListener(ApplicationReadyEvent.class)
    public void seed() {
        if (!service.list().isEmpty()) {
            return;
        }
        StrategyDTO balanced = new StrategyDTO();
        balanced.setName("balanced");
        balanced.setDescription("All 5 strategies on; default 6k char budget.");
        service.create(balanced);

        StrategyDTO lean = new StrategyDTO();
        lean.setName("lean");
        lean.setDescription("Selection + format only; tighter 3k budget for cheap models.");
        lean.setCompressionEnabled(false);
        lean.setOrderingEnabled(false);
        lean.setCharBudget(3000);
        service.create(lean);
        log.info("Seeded default CEF strategies: balanced, lean");
    }
}
