package com.jk.labs.vkp.datacollection.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.jk.labs.vkp.datacollection.common.dto.register.RegisterSnapshotCtx;
import com.jk.labs.vkp.datacollection.common.dto.register.RegisterSnapshotReqDTO;
import com.jk.labs.vkp.datacollection.common.dto.snapshot.ListSnapshotsCtx;
import com.jk.labs.vkp.datacollection.common.dto.snapshot.ListSnapshotsReqDTO;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.HashMap;
import java.util.Map;

/**
 * On startup, repopulates {@code company_resource_graph} SNAPSHOT_PAGE rows from the DURABLE
 * filesystem snapshots, so the graph isn't empty after an (in-memory H2) restart. Idempotent —
 * already-registered pages are skipped. Best-effort: if company-service isn't up yet, it logs and
 * skips (a manual register or the next restart will catch up).
 */
@Component
@Slf4j
@RequiredArgsConstructor
public class SnapshotGraphBootstrap {

    private final SnapshotService snapshotService;
    private final DataCollectionService dataCollectionService;

    /** company-service URL for the host-run service (NOT the container host.docker.internal used by DAGs). */
    @Value("${datacollection.company-service-url:http://localhost:8081}")
    private String companyServiceUrl;

    @Value("${datacollection.auto-register-snapshots:true}")
    private boolean enabled;

    @EventListener(ApplicationReadyEvent.class)
    public void onReady() {
        if (!enabled) {
            return;
        }
        try {
            Map<String, String> nameToId = fetchCompanies();
            if (nameToId.isEmpty()) {
                log.info("auto-register: no companies from company-service yet — skipping snapshot bootstrap");
                return;
            }
            ListSnapshotsCtx ctx = new ListSnapshotsCtx();
            ctx.setReqDTO(new ListSnapshotsReqDTO());
            snapshotService.listCompanies(ctx);

            int registered = 0;
            int companies = 0;
            for (var snap : ctx.getRespDTO().getCompanies()) {
                String companyId = nameToId.get(snap.getCompany());
                if (companyId == null) {
                    continue;
                }
                RegisterSnapshotCtx rc = new RegisterSnapshotCtx();
                rc.setReqDTO(new RegisterSnapshotReqDTO(companyId, snap.getCompany(), null, "startup-bootstrap"));
                dataCollectionService.registerSnapshotAsGraph(rc);
                registered += rc.getRespDTO().getRegistered();
                companies++;
            }
            log.info("auto-register: {} snapshot company(ies) processed, {} new graph row(s) on startup",
                    companies, registered);
        } catch (Exception e) {  // noqa
            log.warn("auto-register snapshots on startup failed (company-service down?): {}", e.getMessage());
        }
    }

    private Map<String, String> fetchCompanies() {
        JsonNode resp = RestClient.create().get()
                .uri(companyServiceUrl + "/admin/company/service/v1/crud/companies")
                .retrieve().body(JsonNode.class);
        Map<String, String> map = new HashMap<>();
        if (resp != null && resp.has("companies")) {
            for (JsonNode c : resp.get("companies")) {
                map.put(c.path("name").asText(), c.path("companyId").asText());
            }
        }
        return map;
    }
}
