package com.jk.labs.vkp.indexing.service;

import com.jk.labs.vkp.indexing.common.error.AirflowGatewayException;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/**
 * Calls the horizontally-scalable Spring-AI executor (indexing-service-wfs-java) over HTTP.
 * The executor runs async and reports terminal status back via the control-plane callback.
 */
@Component
public class WfsClient {

    private final RestClient rest;

    public WfsClient(IndexingProperties props) {
        this.rest = RestClient.builder()
                .baseUrl(props.getWfsBaseUrl())
                .defaultHeaders(h -> h.setContentType(MediaType.APPLICATION_JSON))
                .build();
    }

    /** Abstract executor invocation: (executorId, indexLogId, runtimeParams). Returns immediately. */
    public void execute(String executorId, String indexLogId, Map<String, Object> runtimeParams) {
        Map<String, Object> body = new HashMap<>();
        body.put("indexLogId", indexLogId);
        body.put("runtimeParams", runtimeParams == null ? Map.of() : runtimeParams);
        try {
            rest.post().uri("/wfs/{ref}/execute", executorId).body(body).retrieve().toBodilessEntity();
        } catch (RestClientException e) {
            throw new AirflowGatewayException("Failed to reach indexing-service-wfs-java: " + e.getMessage(), e);
        }
    }

    public static Map<String, Object> params(String companyId, List<String> docIds, String scope) {
        Map<String, Object> m = new HashMap<>();
        m.put("companyId", companyId);
        m.put("scope", scope);
        m.put("docIds", docIds == null ? List.of() : docIds);
        return m;
    }
}
