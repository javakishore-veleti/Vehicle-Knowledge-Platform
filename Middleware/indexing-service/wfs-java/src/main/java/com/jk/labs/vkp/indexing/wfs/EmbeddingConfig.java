package com.jk.labs.vkp.indexing.wfs;

import org.springframework.ai.transformers.TransformersEmbeddingModel;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/**
 * Local ONNX embedding model — Spring AI's {@link TransformersEmbeddingModel} defaults to
 * sentence-transformers/all-MiniLM-L6-v2 (384 dims, no API key). It implements
 * {@code InitializingBean}, so Spring calls {@code afterPropertiesSet()} (which loads the
 * tokenizer + ONNX model, caching under the configured dir) during context init.
 */
@Configuration
public class EmbeddingConfig {

    @Bean
    public TransformersEmbeddingModel embeddingModel() {
        TransformersEmbeddingModel model = new TransformersEmbeddingModel();
        model.setResourceCacheDirectory(System.getProperty("java.io.tmpdir") + "/vkp-onnx-cache");
        return model;
    }
}
