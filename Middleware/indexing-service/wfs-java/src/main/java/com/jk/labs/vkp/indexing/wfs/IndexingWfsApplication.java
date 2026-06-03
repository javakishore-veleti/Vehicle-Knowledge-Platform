package com.jk.labs.vkp.indexing.wfs;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

/**
 * indexing-service-wfs-java (port 8087): the horizontally-scalable Spring-AI executor.
 * The control plane (indexing-service) invokes {@code POST /wfs/{executorId}/execute};
 * execution runs async and reports terminal status back via the control-plane callback.
 *
 * Phase 1: stub executor (no embedding yet). Phase 2 wires Spring AI TransformersEmbeddingModel
 * -> PgVectorStore.
 */
@SpringBootApplication
@EnableAsync
public class IndexingWfsApplication {

    public static void main(String[] args) {
        SpringApplication.run(IndexingWfsApplication.class, args);
    }
}
