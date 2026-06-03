package com.jk.labs.vkp.indexing.wfs;

import org.springframework.ai.document.MetadataMode;
import org.springframework.ai.embedding.EmbeddingModel;
import org.springframework.ai.openai.OpenAiEmbeddingModel;
import org.springframework.ai.openai.OpenAiEmbeddingOptions;
import org.springframework.ai.openai.api.OpenAiApi;
import org.springframework.ai.transformers.TransformersEmbeddingModel;
import org.springframework.stereotype.Component;

import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.ConcurrentMap;

/**
 * Resolves the embedding model for a formula's provider:
 *  - {@code sentence-transformers} (default) -> local ONNX {@link TransformersEmbeddingModel} (384d, no key)
 *  - {@code openai} -> {@link OpenAiEmbeddingModel} (text-embedding-3-*, needs OPENAI_API_KEY)
 * OpenAI models are built lazily and cached per model name (so no key is needed unless used).
 */
@Component
public class EmbeddingModels {

    private static final String DEFAULT_OPENAI_MODEL = "text-embedding-3-small";

    private final TransformersEmbeddingModel sentenceTransformers;
    private final ConcurrentMap<String, EmbeddingModel> openaiByModel = new ConcurrentHashMap<>();

    public EmbeddingModels(TransformersEmbeddingModel sentenceTransformers) {
        this.sentenceTransformers = sentenceTransformers;
    }

    public EmbeddingModel resolve(String provider, String model) {
        if ("openai".equalsIgnoreCase(provider)) {
            return openaiByModel.computeIfAbsent(model == null ? DEFAULT_OPENAI_MODEL : model, this::openai);
        }
        return sentenceTransformers;   // sentence-transformers + default
    }

    private EmbeddingModel openai(String model) {
        String key = System.getenv("OPENAI_API_KEY");
        if (key == null || key.isBlank()) {
            throw new IllegalStateException("OPENAI_API_KEY is not set; cannot use the OpenAI embedding provider");
        }
        OpenAiApi api = OpenAiApi.builder().apiKey(key).build();
        OpenAiEmbeddingOptions opts = OpenAiEmbeddingOptions.builder().model(model).build();
        return new OpenAiEmbeddingModel(api, MetadataMode.EMBED, opts);
    }
}
