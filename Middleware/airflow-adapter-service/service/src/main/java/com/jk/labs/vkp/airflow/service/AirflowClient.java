package com.jk.labs.vkp.airflow.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.jk.labs.vkp.airflow.common.dto.DagRunDTO;
import com.jk.labs.vkp.airflow.common.dto.TaskInstanceDTO;
import com.jk.labs.vkp.airflow.common.error.AirflowGatewayException;
import com.jk.labs.vkp.airflow.common.error.ResourceNotFoundException;
import org.springframework.http.HttpStatusCode;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.UUID;

/**
 * The single HTTP client for Apache Airflow's stable REST API (v1). All Airflow-specific
 * knowledge (endpoints, basic auth, payload shapes, retry-by-clear, cancel-by-state) lives
 * here so no other service duplicates it.
 */
@Component
public class AirflowClient {

    private final RestClient rest;
    private final ObjectMapper mapper;

    public AirflowClient(AirflowProperties props, ObjectMapper mapper) {
        this.mapper = mapper;
        this.rest = RestClient.builder()
                .baseUrl(props.getBaseUrl())
                .defaultHeaders(h -> {
                    h.setBasicAuth(props.getUsername(), props.getPassword());
                    h.setContentType(MediaType.APPLICATION_JSON);
                })
                .build();
    }

    public DagRunDTO triggerDagRun(String dagId, Map<String, Object> conf, String note) {
        Map<String, Object> body = new HashMap<>();
        body.put("dag_run_id", "adapter__" + UUID.randomUUID());
        body.put("conf", conf == null ? Map.of() : conf);
        if (note != null) {
            body.put("note", note);
        }
        JsonNode resp = execute(rest.post().uri("/api/v1/dags/{d}/dagRuns", dagId).body(body),
                "DAG not found: " + dagId);
        return toDagRun(resp);
    }

    public DagRunDTO getDagRun(String dagId, String runId) {
        JsonNode resp = execute(rest.get().uri("/api/v1/dags/{d}/dagRuns/{r}", dagId, runId),
                "DAG run not found: " + dagId + "/" + runId);
        return toDagRun(resp);
    }

    public List<TaskInstanceDTO> getTaskInstances(String dagId, String runId) {
        JsonNode resp = execute(rest.get().uri("/api/v1/dags/{d}/dagRuns/{r}/taskInstances", dagId, runId),
                "DAG run not found: " + dagId + "/" + runId);
        List<TaskInstanceDTO> tasks = new ArrayList<>();
        JsonNode arr = resp.get("task_instances");
        if (arr != null && arr.isArray()) {
            arr.forEach(n -> tasks.add(toTask(n)));
        }
        return tasks;
    }

    /** Retry = clear the run's task instances so Airflow re-runs them. */
    public DagRunDTO clearDagRun(String dagId, String runId) {
        JsonNode resp = execute(
                rest.post().uri("/api/v1/dags/{d}/dagRuns/{r}/clear", dagId, runId).body(Map.of("dry_run", false)),
                "DAG run not found: " + dagId + "/" + runId);
        return toDagRun(resp);
    }

    /** Cancel = set the run's state (e.g. "failed") via PATCH. */
    public DagRunDTO setDagRunState(String dagId, String runId, String state) {
        JsonNode resp = execute(
                rest.patch().uri("/api/v1/dags/{d}/dagRuns/{r}", dagId, runId).body(Map.of("state", state)),
                "DAG run not found: " + dagId + "/" + runId);
        return toDagRun(resp);
    }

    private JsonNode execute(RestClient.RequestHeadersSpec<?> spec, String notFoundMsg) {
        try {
            return spec.retrieve()
                    .onStatus(status -> status.value() == 404, (req, res) -> {
                        throw new ResourceNotFoundException(notFoundMsg);
                    })
                    .onStatus(HttpStatusCode::isError, (req, res) -> {
                        throw new AirflowGatewayException("Airflow returned " + res.getStatusCode());
                    })
                    .body(JsonNode.class);
        } catch (ResourceNotFoundException | AirflowGatewayException e) {
            throw e;
        } catch (RestClientException e) {
            throw new AirflowGatewayException("Failed to reach Airflow: " + e.getMessage(), e);
        }
    }

    private DagRunDTO toDagRun(JsonNode n) {
        return DagRunDTO.builder()
                .dagId(text(n, "dag_id"))
                .dagRunId(text(n, "dag_run_id"))
                .state(text(n, "state"))
                .logicalDate(text(n, "logical_date"))
                .startDate(text(n, "start_date"))
                .endDate(text(n, "end_date"))
                .note(text(n, "note"))
                .conf(confMap(n))
                .build();
    }

    private TaskInstanceDTO toTask(JsonNode n) {
        return TaskInstanceDTO.builder()
                .taskId(text(n, "task_id"))
                .state(text(n, "state"))
                .tryNumber(n.hasNonNull("try_number") ? n.get("try_number").asInt() : null)
                .startDate(text(n, "start_date"))
                .endDate(text(n, "end_date"))
                .build();
    }

    @SuppressWarnings("unchecked")
    private Map<String, Object> confMap(JsonNode n) {
        JsonNode conf = n.get("conf");
        if (conf == null || !conf.isObject()) {
            return null;
        }
        return mapper.convertValue(conf, Map.class);
    }

    private static String text(JsonNode n, String field) {
        return n != null && n.hasNonNull(field) ? n.get(field).asText() : null;
    }
}
