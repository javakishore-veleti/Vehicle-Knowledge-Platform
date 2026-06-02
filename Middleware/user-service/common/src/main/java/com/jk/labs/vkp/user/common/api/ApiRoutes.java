package com.jk.labs.vkp.user.common.api;

import lombok.AccessLevel;
import lombok.NoArgsConstructor;

/**
 * Centralized, versioned API route prefixes for the customer-facing user service.
 *
 * Convention: {@code /<audience>/<domain>/service/v<major>/<group>/<resource>}.
 * Here the audience is {@code customer} (Vehicle Search Portal end-users).
 */
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public final class ApiRoutes {

    /** Versioned base for this microservice. */
    public static final String API_BASE = "/customer/user/service/v1";

    /** Authentication group: signup, signin, password reset. */
    public static final String AUTH = API_BASE + "/auth";

    /** Profile group: read / update the current user's profile. */
    public static final String PROFILE = API_BASE + "/profile";
}
