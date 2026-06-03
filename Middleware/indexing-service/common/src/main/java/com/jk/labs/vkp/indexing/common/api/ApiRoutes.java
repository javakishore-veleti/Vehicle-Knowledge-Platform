package com.jk.labs.vkp.indexing.common.api;

import lombok.AccessLevel;
import lombok.NoArgsConstructor;

/**
 * Versioned, admin-facing API route prefixes for the indexing control plane.
 * Convention: {@code /<audience>/<domain>/service/v<major>/<resource>}.
 */
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public final class ApiRoutes {

    public static final String API_BASE = "/admin/indexing/service/v1";

    /** Registry / admin listings. */
    public static final String WORKFLOWS = API_BASE + "/workflows";
    public static final String FORMULAS = API_BASE + "/formulas";
    public static final String CREDENTIALS = API_BASE + "/credentials";

    /** Trigger an indexing run for a company. */
    public static final String TRIGGER = API_BASE + "/companies/{companyId}/index";

    /** Index logs (ledger) for a company. */
    public static final String LOGS = API_BASE + "/companies/{companyId}/index-logs";

    /** Executor callback to update a log's status. */
    public static final String CALLBACK = API_BASE + "/index-logs/{indexLogId}/callback";
}
