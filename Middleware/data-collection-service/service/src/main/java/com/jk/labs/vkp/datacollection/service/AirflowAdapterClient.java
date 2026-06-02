package com.jk.labs.vkp.datacollection.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.jk.labs.vkp.datacollection.common.error.AirflowGatewayException;
import com.jk.labs.vkp.datacollection.common.error.ResourceNotFoundException;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.util.HashMap;
import java.util.Map;

/**
 * HTTP client for airflow-adapter-service. This service NEVER calls Airflow directly —
 * all DAG operations go through the adapter (single Airflow gateway).
 */
@Component
public class AirflowAdapterClient {

    private static final String RUNS = "/internal/airflow/service/v1/dags/{dagId}/runs";
    private static final String RUN = RUNS + "/{runId}";

    private final RestClient rest;

    public AirflowAdapterClient(AirflowAdapterProperties props) {
        this.rest = RestClient.builder()
                .baseUrl(props.getBaseUrl())
                .defaultHeaders(h -> h.setContentType(MediaType.APPLICATION_JSON))
                .build();
    }

    /** Reference to a DAG run as returned by the adapter. */
    public record DagRunRef(String dagId, String dagRunId, String state) {
    }

    public DagRunRef triggerDag(String dagId, Map<String, Object> conf, String triggeredBy) {
        Map<String, Object> body = new HashMap<>();
        body.put("conf", conf);
        body.put("triggeredBy", triggeredBy);
        body.put("runType", "ON_DEMAND");
        JsonNode resp = execute(rest.post().uri(RUNS, dagId).body(body), "DAG not found: " + dagId);
        return toRef(resp);
    }

    public DagRunRef getRun(String dagId, String runId) {
        JsonNode resp = execute(rest.get().uri(RUN, dagId, runId),
                "DAG run not found: " + dagId + "/" + runId);
        return toRef(resp);
    }

    private JsonNode execute(RestClient.RequestHeadersSpec<?> spec, String notFoundMsg) {
        try {
            return spec.retrieve()
                    .onStatus(s -> s.value() == 404, (req, res) -> {
                        throw new ResourceNotFoundException(notFoundMsg);
                    })
                    .onStatus(HttpStatusCode::isError, (req, res) -> {
                        throw new AirflowGatewayException("airflow-adapter returned " + res.getStatusCode());
                    })
                    .body(JsonNode.class);
        } catch (ResourceNotFoundException | AirflowGatewayException e) {
            throw e;
        } catch (RestClientException e) {
            throw new AirflowGatewayException("Failed to reach airflow-adapter-service: " + e.getMessage(), e);
        }
    }

    private DagRunRef toRef(JsonNode resp) {
        JsonNode run = resp == null ? null : resp.get("dagRun");
        if (run == null) {
            throw new AirflowGatewayException("Malformed adapter response (missing dagRun)");
        }
        return new DagRunRef(text(run, "dagId"), text(run, "dagRunId"), text(run, "state"));
    }

    private static String text(JsonNode n, String field) {
        return n != null && n.hasNonNull(field) ? n.get(field).asText() : null;
    }
}
