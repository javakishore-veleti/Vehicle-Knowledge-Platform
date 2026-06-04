package com.jk.labs.vkp.security;

import java.util.Optional;

/** Per-request access to the decrypted {@link SessionContext} (set/cleared by the filter). */
public final class SessionContextHolder {

    private static final ThreadLocal<SessionContext> CTX = new ThreadLocal<>();

    private SessionContextHolder() {
    }

    public static void set(SessionContext ctx) {
        CTX.set(ctx);
    }

    public static SessionContext get() {
        return CTX.get();
    }

    public static Optional<SessionContext> current() {
        return Optional.ofNullable(CTX.get());
    }

    public static void clear() {
        CTX.remove();
    }
}
