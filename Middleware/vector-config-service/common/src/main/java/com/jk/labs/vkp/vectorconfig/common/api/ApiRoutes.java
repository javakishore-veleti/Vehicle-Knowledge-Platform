package com.jk.labs.vkp.vectorconfig.common.api;

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
    public static final String API_BASE = "/admin/vector-config/service/v1";

    /** CRUD operation group. */
    public static final String CRUD = API_BASE + "/crud";

    /** Vector-config collection (flat: get/update/delete/list by id). */
    public static final String VECTOR_CONFIGS = CRUD + "/vector-configs";

    /** Vector configs nested under a company resource (create + list-for-resource). */
    public static final String RESOURCE_VECTOR_CONFIGS =
            CRUD + "/company-resources/{companyResourceId}/vector-configs";
}
