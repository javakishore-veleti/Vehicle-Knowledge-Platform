package com.jk.labs.vkp.rbac;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;

import java.util.ArrayList;
import java.util.List;

/**
 * Config for the JWT/RBAC filter, prefix {@code vkp.jwt}.
 *
 * <p>RBAC is derived from the request path's audience segment:
 * {@code /admin/**} requires role ADMIN, {@code /customer/**} requires any authenticated user,
 * {@code /internal/**} is service-to-service (permitted, or gated by {@code internalApiKey}).
 * Swagger/actuator/error are always public; {@link #permitPatterns} adds service-specific public
 * paths (auth endpoints, DAG callbacks) as Ant patterns.
 */
@Getter
@Setter
@ConfigurationProperties(prefix = "vkp.jwt")
public class JwtRbacProperties {

    /** Master switch. When false the filter is a no-op (validates nothing, blocks nothing). */
    private boolean enabled = true;

    /** HS256 signing secret — MUST equal user-service's jwt.secret (same JWT_SECRET env). */
    private String secret = "change-me-dev-secret-please-override-in-prod-0123456789";

    /** Header carrying the bearer token. */
    private String header = "Authorization";

    /** JWT claim that holds the role (USER | ADMIN). */
    private String roleClaim = "role";

    /** Ant patterns that bypass auth entirely (e.g. /customer/user/service/v1/auth/**, callbacks). */
    private List<String> permitPatterns = new ArrayList<>();

    /** Optional shared secret required (header {@code X-VKP-Internal-Key}) for /internal/** calls.
     *  Blank => /internal/** is permitted without a key (localhost dev). */
    private String internalApiKey = "";
}
