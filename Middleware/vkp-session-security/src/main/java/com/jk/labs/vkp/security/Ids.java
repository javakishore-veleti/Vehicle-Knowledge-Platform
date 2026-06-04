package com.jk.labs.vkp.security;

import java.util.UUID;

/** Generates the platform's session and query ids (prefixed UUIDv4, no dashes). */
public final class Ids {

    private Ids() {
    }

    public static String newSessionId() {
        return "ses_" + UUID.randomUUID().toString().replace("-", "");
    }

    public static String newQueryId() {
        return "qry_" + UUID.randomUUID().toString().replace("-", "");
    }
}
