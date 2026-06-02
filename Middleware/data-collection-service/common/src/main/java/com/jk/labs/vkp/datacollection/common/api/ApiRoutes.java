package com.jk.labs.vkp.datacollection.common.api;

import lombok.AccessLevel;
import lombok.NoArgsConstructor;

/**
 * Versioned, admin-facing API route prefixes.
 * Convention: {@code /<audience>/<domain>/service/v<major>/<resource>}.
 */
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public final class ApiRoutes {

    public static final String API_BASE = "/admin/data-collection/service/v1";

    /** Trigger link discovery for a company resource. */
    public static final String DISCOVER =
            API_BASE + "/companies/{companyId}/resources/{resourceId}/discover";

    /** Read the discovered resource-graph nodes for a company. */
    public static final String RESOURCE_GRAPH = API_BASE + "/companies/{companyId}/resource-graph";

    /** Read the status of a discovery DAG run (proxied via the adapter). */
    public static final String RUN_STATUS = API_BASE + "/runs/{dagId}/{runId}/status";
}
