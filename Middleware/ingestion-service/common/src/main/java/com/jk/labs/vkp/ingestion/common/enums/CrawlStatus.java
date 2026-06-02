package com.jk.labs.vkp.ingestion.common.enums;

/** Discovery/crawl status of a resource-graph node. */
public enum CrawlStatus {
    PENDING,
    DISCOVERING,
    DISCOVERED,
    FAILED;

    public static final String DEFAULT = PENDING.name();
}
