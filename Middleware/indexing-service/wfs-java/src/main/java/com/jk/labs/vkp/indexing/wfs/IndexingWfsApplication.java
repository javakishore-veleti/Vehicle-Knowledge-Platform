package com.jk.labs.vkp.indexing.wfs;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableAsync;

/**
 * indexing-service-wfs-java (port 8087): the horizontally-scalable Spring-AI executor.
 * The control plane (indexing-service) invokes {@code POST /wfs/{executorId}/execute};
 * execution runs async and reports terminal status back via the control-plane callback.
 *
 * Real Spring-AI executor: chunks content, embeds via TransformersEmbeddingModel
 * (sentence-transformers/all-MiniLM-L6-v2, 384d; provider-pluggable) and writes vectors to the
 * configured store (pgVector / Mongo).
 */
@SpringBootApplication
@EnableAsync
public class IndexingWfsApplication {

    public static void main(String[] args) {
        SpringApplication.run(IndexingWfsApplication.class, args);
    }
}
