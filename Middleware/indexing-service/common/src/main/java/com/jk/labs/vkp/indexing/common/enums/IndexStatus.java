package com.jk.labs.vkp.indexing.common.enums;

/** Lifecycle of a resource_graph_index_log row. */
public enum IndexStatus {
    PENDING,
    IN_PROGRESS,
    INDEXED,
    FAILED,
    SKIPPED
}
