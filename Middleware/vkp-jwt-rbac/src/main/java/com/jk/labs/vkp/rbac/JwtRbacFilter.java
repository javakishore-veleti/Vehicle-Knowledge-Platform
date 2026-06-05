package com.jk.labs.vkp.rbac;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.util.AntPathMatcher;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.List;

/**
 * Validates the bearer JWT and enforces route-audience RBAC:
 * <ul>
 *   <li>{@code /admin/**}    -> requires a valid token with role ADMIN (else 401/403)</li>
 *   <li>{@code /customer/**} -> requires any valid token (else 401)</li>
 *   <li>{@code /internal/**} -> service-to-service: permitted, or gated by X-VKP-Internal-Key</li>
 *   <li>swagger/actuator/error + configured permit patterns -> public</li>
 * </ul>
 * The validated {@link JwtPrincipal} is exposed via {@link JwtAuthContextHolder} + request attribute.
 */
@Slf4j
public class JwtRbacFilter extends OncePerRequestFilter {

    public static final String ATTR = "vkp.jwt.principal";
    public static final String INTERNAL_KEY_HEADER = "X-VKP-Internal-Key";
    private static final String BEARER = "Bearer ";

    /** Always-public infra paths (no auth), regardless of audience. */
    private static final String[] DEFAULT_PUBLIC = {
            "/swagger-ui/**", "/swagger-ui.html", "/v3/api-docs/**", "/v3/api-docs",
            "/actuator/**", "/error", "/favicon.ico"
    };

    /** What a path requires. Package-private + derived by a pure function, so it is unit-testable. */
    enum Access { PUBLIC, INTERNAL, AUTH, ADMIN }

    private final JwtService jwt;
    private final JwtRbacProperties props;
    private final AntPathMatcher matcher = new AntPathMatcher();

    public JwtRbacFilter(JwtService jwt, JwtRbacProperties props) {
        this.jwt = jwt;
        this.props = props;
    }

    /** Pure RBAC decision for a request path given the service's permit patterns. */
    static Access access(String path, List<String> permitPatterns, AntPathMatcher matcher) {
        for (String p : DEFAULT_PUBLIC) {
            if (matcher.match(p, path)) {
                return Access.PUBLIC;
            }
        }
        for (String p : permitPatterns) {
            if (matcher.match(p, path)) {
                return Access.PUBLIC;
            }
        }
        if (path.startsWith("/internal/")) {
            return Access.INTERNAL;
        }
        if (path.startsWith("/admin/")) {
            return Access.ADMIN;
        }
        if (path.startsWith("/customer/")) {
            return Access.AUTH;
        }
        return Access.PUBLIC;   // non-audience paths (root, etc.) — nothing sensitive
    }

    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain)
            throws ServletException, IOException {
        if (!props.isEnabled()) {
            chain.doFilter(req, res);
            return;
        }
        String path = req.getRequestURI();
        Access access = access(path, props.getPermitPatterns(), matcher);

        if (access == Access.PUBLIC) {
            chain.doFilter(req, res);
            return;
        }
        if (access == Access.INTERNAL) {
            String required = props.getInternalApiKey();
            if (required != null && !required.isBlank()
                    && !required.equals(req.getHeader(INTERNAL_KEY_HEADER))) {
                res.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Missing or invalid internal key");
                return;
            }
            chain.doFilter(req, res);
            return;
        }

        JwtPrincipal principal = jwt.validate(bearer(req));
        if (principal == null) {
            res.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Missing or invalid bearer token");
            return;
        }
        if (access == Access.ADMIN && !principal.isAdmin()) {
            res.sendError(HttpServletResponse.SC_FORBIDDEN, "Requires ADMIN role");
            return;
        }
        try {
            JwtAuthContextHolder.set(principal);
            req.setAttribute(ATTR, principal);
            chain.doFilter(req, res);
        } finally {
            JwtAuthContextHolder.clear();
        }
    }

    private String bearer(HttpServletRequest req) {
        String raw = req.getHeader(props.getHeader());
        if (raw == null || raw.isBlank()) {
            return null;
        }
        return raw.startsWith(BEARER) ? raw.substring(BEARER.length()).trim() : raw.trim();
    }
}
