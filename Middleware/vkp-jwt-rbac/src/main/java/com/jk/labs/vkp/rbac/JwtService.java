package com.jk.labs.vkp.rbac;

import io.jsonwebtoken.Claims;
import io.jsonwebtoken.Jws;
import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;

/**
 * Validates the user-service HS256 JWT and extracts a {@link JwtPrincipal}. The signing secret
 * MUST match user-service's {@code jwt.secret} (same {@code JWT_SECRET} env across services). jjwt
 * verifies the signature + {@code exp} automatically; a bad/expired/tampered token throws.
 */
public class JwtService {

    private final SecretKey key;
    private final String roleClaim;

    public JwtService(String secret, String roleClaim) {
        this.key = Keys.hmacShaKeyFor(secret.getBytes(StandardCharsets.UTF_8));
        this.roleClaim = roleClaim;
    }

    /** @return the validated principal, or {@code null} if the token is missing/invalid/expired. */
    public JwtPrincipal validate(String token) {
        if (token == null || token.isBlank()) {
            return null;
        }
        try {
            Jws<Claims> jws = Jwts.parser().verifyWith(key).build().parseSignedClaims(token);
            Claims c = jws.getPayload();
            return new JwtPrincipal(c.getSubject(), c.get("email", String.class), c.get(roleClaim, String.class));
        } catch (RuntimeException e) {
            return null;
        }
    }
}
