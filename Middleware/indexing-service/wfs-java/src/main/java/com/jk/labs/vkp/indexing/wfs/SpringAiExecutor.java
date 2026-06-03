package com.jk.labs.vkp.indexing.wfs;

import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.scheduling.annotation.Async;
import org.springframework.stereotype.Service;

import java.util.Map;

/**
 * Runs an indexing workflow asynchronously and reports status back to the control plane.
 *
 * Phase 1: STUB — marks IN_PROGRESS then INDEXED (chunks=0), no embedding.
 * Phase 2: load the company's snapshot docs, chunk + embed with Spring AI
 * (TransformersEmbeddingModel), and write to the configured vector store (PgVectorStore).
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class SpringAiExecutor {

    private final WfsControlClient control;

    @Async
    public void execute(String executorId, String indexLogId, Map<String, Object> runtimeParams) {
        log.info("Executor '{}' starting for log {} (params={})", executorId, indexLogId, runtimeParams);
        control.callback(indexLogId, "IN_PROGRESS", null, null, "wfs-" + indexLogId);
        try {
            // Phase 2: real chunk + embed + vector-store write goes here.
            int chunks = 0;
            control.callback(indexLogId, "INDEXED", chunks, null, "wfs-" + indexLogId);
            log.info("Executor '{}' completed (stub) for log {}", executorId, indexLogId);
        } catch (Exception e) {  // noqa
            log.error("Executor '{}' failed for log {}", executorId, indexLogId, e);
            control.callback(indexLogId, "FAILED", null, e.getMessage(), "wfs-" + indexLogId);
        }
    }
}
