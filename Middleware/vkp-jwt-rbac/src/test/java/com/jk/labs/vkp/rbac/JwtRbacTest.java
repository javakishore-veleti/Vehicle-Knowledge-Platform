package com.jk.labs.vkp.rbac;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import org.junit.jupiter.api.Test;
import org.springframework.util.AntPathMatcher;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Date;
import java.util.List;

import static org.junit.jupiter.api.Assertions.*;

class JwtRbacTest {

    private static final String SECRET = "change-me-dev-secret-please-override-in-prod-0123456789";
    private final JwtService jwt = new JwtService(SECRET, "role");

    private static String token(String secret, String userId, String email, String role, long minutes) {
        SecretKey key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        Instant now = Instant.now();
        return Jwts.builder().subject(userId).claim("email", email).claim("role", role)
                .issuedAt(Date.from(now)).expiration(Date.from(now.plus(minutes, ChronoUnit.MINUTES)))
                .signWith(key).compact();
    }

    @Test
    void validatesAGoodTokenAndExtractsRole() {
        JwtPrincipal p = jwt.validate(token(SECRET, "u1", "a@b.com", "ADMIN", 60));
        assertNotNull(p);
        assertEquals("u1", p.userId());
        assertEquals("a@b.com", p.email());
        assertTrue(p.isAdmin());
    }

    @Test
    void userRoleIsNotAdmin() {
        JwtPrincipal p = jwt.validate(token(SECRET, "u2", "c@d.com", "USER", 60));
        assertNotNull(p);
        assertFalse(p.isAdmin());
    }

    @Test
    void rejectsExpiredToken() {
        assertNull(jwt.validate(token(SECRET, "u1", "a@b.com", "ADMIN", -5)));
    }

    @Test
    void rejectsTokenSignedWithWrongSecret() {
        String forged = token("a-totally-different-secret-key-0123456789-xxxx", "u1", "a@b.com", "ADMIN", 60);
        assertNull(jwt.validate(forged));
    }

    @Test
    void rejectsNullAndBlank() {
        assertNull(jwt.validate(null));
        assertNull(jwt.validate("   "));
        assertNull(jwt.validate("not.a.jwt"));
    }

    @Test
    void rbacPolicyByAudience() {
        AntPathMatcher m = new AntPathMatcher();
        List<String> permit = List.of("/customer/user/service/v1/auth/**",
                "/admin/indexing/service/v1/index-logs/*/callback");

        assertEquals(JwtRbacFilter.Access.ADMIN, JwtRbacFilter.access("/admin/indexing/service/v1/workflows", permit, m));
        assertEquals(JwtRbacFilter.Access.AUTH, JwtRbacFilter.access("/customer/user/service/v1/profile/u1", permit, m));
        assertEquals(JwtRbacFilter.Access.INTERNAL, JwtRbacFilter.access("/internal/airflow/service/v1/dags/x/runs", permit, m));
        // permit patterns win over audience
        assertEquals(JwtRbacFilter.Access.PUBLIC, JwtRbacFilter.access("/customer/user/service/v1/auth/signin", permit, m));
        assertEquals(JwtRbacFilter.Access.PUBLIC, JwtRbacFilter.access("/admin/indexing/service/v1/index-logs/abc/callback", permit, m));
        // infra is always public
        assertEquals(JwtRbacFilter.Access.PUBLIC, JwtRbacFilter.access("/actuator/health", permit, m));
        assertEquals(JwtRbacFilter.Access.PUBLIC, JwtRbacFilter.access("/swagger-ui/index.html", permit, m));
    }
}
