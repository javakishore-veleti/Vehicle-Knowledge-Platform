package com.jk.labs.vkp.cef.admin.api;

import com.fasterxml.jackson.databind.ObjectMapper;
import lombok.RequiredArgsConstructor;
import lombok.SneakyThrows;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.web.bind.annotation.*;

import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.time.Duration;
import java.util.List;
import java.util.Map;
import java.util.regex.Pattern;

/** Eval harness — runs a golden query through the context-engine orchestrator and scorecards the
 *  result (groundedness = does the answer cite the assembled sources). */
@RestController
@RequestMapping("/admin/context-engine/service/v1/eval")
@RequiredArgsConstructor
public class EvalController {

    private static final Pattern CITATION = Pattern.compile("\\[\\d+]");
    // HTTP/1.1 — uvicorn (the context-engine) is HTTP/1.1 only; the default HTTP/2 h2c upgrade drops the body.
    private static final HttpClient HTTP = HttpClient.newBuilder().version(HttpClient.Version.HTTP_1_1).build();

    private final ObjectMapper mapper;

    @Value("${cef.engine-url:http://localhost:8093}")
    private String engineUrl;

    @PostMapping("/run")
    @SneakyThrows
    @SuppressWarnings("unchecked")
    public Map<String, Object> run(@RequestBody Map<String, Object> req) {
        HttpRequest httpReq = HttpRequest.newBuilder(URI.create(engineUrl + "/context-engine/orchestrate"))
                .header("Content-Type", "application/json")
                .timeout(Duration.ofSeconds(120))
                .POST(HttpRequest.BodyPublishers.ofString(mapper.writeValueAsString(req)))
                .build();
        Map<String, Object> result = mapper.readValue(
                HTTP.send(httpReq, HttpResponse.BodyHandlers.ofString()).body(), Map.class);

        String answer = String.valueOf(result.getOrDefault("answer", ""));
        List<?> sources = (List<?>) result.getOrDefault("sources", List.of());
        long citations = CITATION.matcher(answer).results().count();
        return Map.of(
                "query", req.get("query"),
                "answer", answer,
                "scorecard", Map.of(
                        "sourceCount", sources.size(),
                        "citationCount", citations,
                        "grounded", citations > 0 && !sources.isEmpty(),
                        "latencyMs", result.getOrDefault("latencyMs", -1)),
                "context", result.getOrDefault("context", Map.of()));
    }
}
