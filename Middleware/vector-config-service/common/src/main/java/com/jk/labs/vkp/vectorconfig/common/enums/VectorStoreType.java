package com.jk.labs.vkp.vectorconfig.common.enums;

import java.util.Arrays;

/**
 * Vector stores a resource may be indexed into (README "Supported Vector Stores").
 * Selection is configuration-driven (architectural rule #3) - never hardcoded.
 */
public enum VectorStoreType {
    MONGODB,
    CHROMADB,
    PGVECTOR,
    WEAVIATE,
    PINECONE;

    /** Case-insensitive membership test for an incoming store-type string. */
    public static boolean isValid(String value) {
        if (value == null || value.isBlank()) {
            return false;
        }
        return Arrays.stream(values()).anyMatch(v -> v.name().equalsIgnoreCase(value.trim()));
    }

    /** Normalizes to the canonical lowercase token (e.g. "PgVector" -> "pgvector"). */
    public static String normalize(String value) {
        return value == null ? null : value.trim().toLowerCase();
    }
}
