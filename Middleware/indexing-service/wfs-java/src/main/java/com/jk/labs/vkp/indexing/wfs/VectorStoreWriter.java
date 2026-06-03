package com.jk.labs.vkp.indexing.wfs;

import java.util.List;

/**
 * A target vector store the executor can write embeddings into. Implementations are selected by
 * {@link #store()} (matching the formula's {@code vector_store}: pgvector | mongodb), so the
 * embedding pipeline stays store-agnostic.
 */
public interface VectorStoreWriter {

    /** One embedded chunk. */
    record Row(String url, int chunkIndex, String text, float[] embedding) {
    }

    /** Store key this writer handles, e.g. {@code pgvector} or {@code mongodb}. */
    String store();

    /** Clean re-index for a company: delete its existing vectors in {@code target}, then insert. */
    void writeCompany(String target, int dim, String companyId, List<Row> rows);
}
