package com.jk.labs.vkp.ingestion.common.api;

import lombok.AccessLevel;
import lombok.NoArgsConstructor;

/**
 * Versioned, admin-facing API route prefixes.
 * Convention: {@code /<audience>/<domain>/service/v<major>/<resource>}.
 */
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public final class ApiRoutes {

    public static final String API_BASE = "/admin/ingestion/service/v1";

    /** Trigger content ingestion (crawl discovered links + extract content) for a resource. */
    public static final String INGEST =
            API_BASE + "/companies/{companyId}/resources/{resourceId}/ingest";

    /** Read the extracted content rows for a company. */
    public static final String CONTENT = API_BASE + "/companies/{companyId}/content";

    /** Callback the ingestion DAG posts extracted content to (persisted). */
    public static final String CONTENT_RECORD = API_BASE + "/content/record";

    /** Read the status of an ingestion DAG run (proxied via the adapter). */
    public static final String RUN_STATUS = API_BASE + "/runs/{dagId}/{runId}/status";

    /** List recent workflow (DAG) runs for the ingestion DAG (proxied via the adapter). */
    public static final String WORKFLOWS = API_BASE + "/workflows/{dagId}";
}
