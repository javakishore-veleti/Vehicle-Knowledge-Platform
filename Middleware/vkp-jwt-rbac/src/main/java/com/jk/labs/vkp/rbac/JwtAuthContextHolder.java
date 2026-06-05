package com.jk.labs.vkp.rbac;

/**
 * ThreadLocal access to the validated {@link JwtPrincipal} for the current request. Set by
 * {@link JwtRbacFilter} and cleared in its finally block. Controllers/services can read the
 * authenticated caller without threading it through method arguments.
 */
public final class JwtAuthContextHolder {

    private static final ThreadLocal<JwtPrincipal> CURRENT = new ThreadLocal<>();

    private JwtAuthContextHolder() {
    }

    public static void set(JwtPrincipal principal) {
        CURRENT.set(principal);
    }

    public static JwtPrincipal get() {
        return CURRENT.get();
    }

    public static void clear() {
        CURRENT.remove();
    }
}
