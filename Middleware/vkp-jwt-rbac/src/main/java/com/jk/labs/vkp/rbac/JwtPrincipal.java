package com.jk.labs.vkp.rbac;

/**
 * The validated identity carried by a user-service JWT: subject (userId), email, and role
 * (USER | ADMIN). Threaded through the request via {@link JwtAuthContextHolder}.
 */
public record JwtPrincipal(String userId, String email, String role) {

    public boolean isAdmin() {
        return "ADMIN".equalsIgnoreCase(role);
    }
}
