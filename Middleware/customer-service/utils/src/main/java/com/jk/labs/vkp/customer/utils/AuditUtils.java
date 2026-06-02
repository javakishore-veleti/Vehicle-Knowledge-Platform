package com.jk.labs.vkp.customer.utils;

import lombok.AccessLevel;
import lombok.NoArgsConstructor;

/** Default values for audit/actor fields when a caller is not supplied. */
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public final class AuditUtils {

    public static final String SYSTEM_ACTOR = "system";

    /** Returns the given actor, or the system default when blank/null. */
    public static String actorOrDefault(String actor) {
        return (actor == null || actor.isBlank()) ? SYSTEM_ACTOR : actor;
    }
}
