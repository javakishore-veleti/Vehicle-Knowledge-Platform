package com.jk.labs.vkp.company.common.api;

import lombok.AccessLevel;
import lombok.NoArgsConstructor;

/**
 * Centralized, versioned API route prefixes.
 *
 * Convention: {@code /admin/<domain>/service/v<major>/<group>/<resource>}. Bumping the
 * version (v1 -> v2) or changing the operation group is a single edit here.
 */
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public final class ApiRoutes {

    /** Versioned base for this microservice. */
    public static final String API_BASE = "/admin/company/service/v1";

    /** CRUD operation group (other groups, e.g. /search, can sit alongside later). */
    public static final String CRUD = API_BASE + "/crud";

    /** Company collection. */
    public static final String COMPANIES = CRUD + "/companies";

    /** Company resources, nested under a company. */
    public static final String COMPANY_RESOURCES = COMPANIES + "/{companyId}/resources";
}
