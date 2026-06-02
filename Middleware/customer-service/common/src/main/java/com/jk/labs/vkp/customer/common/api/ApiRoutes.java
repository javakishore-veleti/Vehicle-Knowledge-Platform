package com.jk.labs.vkp.customer.common.api;

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
    public static final String API_BASE = "/admin/customer/service/v1";

    /** CRUD operation group (other groups, e.g. /search, can sit alongside later). */
    public static final String CRUD = API_BASE + "/crud";

    /** Customer collection. */
    public static final String CUSTOMERS = CRUD + "/customers";

    /** Customer resources, nested under a customer. */
    public static final String CUSTOMER_RESOURCES = CUSTOMERS + "/{customerId}/resources";
}
