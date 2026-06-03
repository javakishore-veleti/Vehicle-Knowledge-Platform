package com.jk.labs.vkp.indexing.wfs;

import lombok.extern.slf4j.Slf4j;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.util.HashMap;
import java.util.Map;

/** Reports a log's terminal status back to the indexing control plane. */
@Component
@Slf4j
public class WfsControlClient {

    private static final String CALLBACK = "/admin/indexing/service/v1/index-logs/{id}/callback";

    private final RestClient rest;

    public WfsControlClient(WfsProperties props) {
        this.rest = RestClient.builder()
                .baseUrl(props.getControlBaseUrl())
                .defaultHeaders(h -> h.setContentType(MediaType.APPLICATION_JSON))
                .build();
    }

    public void callback(String indexLogId, String status, Integer chunks, String error, String runRef) {
        Map<String, Object> body = new HashMap<>();
        body.put("status", status);
        body.put("chunks", chunks);
        body.put("error", error);
        body.put("runRef", runRef);
        try {
            rest.post().uri(CALLBACK, indexLogId).body(body).retrieve().toBodilessEntity();
        } catch (Exception e) {  // noqa
            log.warn("Callback to control plane failed for log {}: {}", indexLogId, e.getMessage());
        }
    }
}
