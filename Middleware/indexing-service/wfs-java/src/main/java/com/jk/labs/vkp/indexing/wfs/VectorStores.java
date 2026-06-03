package com.jk.labs.vkp.indexing.wfs;

import org.springframework.stereotype.Component;

import java.util.HashMap;
import java.util.List;
import java.util.Map;

/** Resolves the {@link VectorStoreWriter} for a formula's vector_store (pgvector | mongodb). */
@Component
public class VectorStores {

    private final Map<String, VectorStoreWriter> byStore = new HashMap<>();

    public VectorStores(List<VectorStoreWriter> writers) {
        for (VectorStoreWriter w : writers) {
            byStore.put(w.store(), w);
        }
    }

    public VectorStoreWriter resolve(String store) {
        String key = (store == null || store.isBlank()) ? "pgvector" : store.toLowerCase();
        VectorStoreWriter w = byStore.get(key);
        if (w == null) {
            throw new IllegalArgumentException("Unknown vector store: " + store + " (known: " + byStore.keySet() + ")");
        }
        return w;
    }
}
