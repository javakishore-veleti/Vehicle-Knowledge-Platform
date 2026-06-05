package com.jk.labs.vkp.user.service;

import io.jsonwebtoken.Jwts;
import io.jsonwebtoken.security.Keys;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import javax.crypto.SecretKey;
import java.nio.charset.StandardCharsets;
import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.Date;

/** Issues signed JWTs for authenticated users. */
@Service
@RequiredArgsConstructor
public class AuthTokenService {

    private final JwtProperties props;

    /** Result of issuing a token. */
    public record IssuedToken(String token, Instant expiresAt) {
    }

    public IssuedToken issue(String userId, String email, String role) {
        Instant now = Instant.now();
        Instant expiresAt = now.plus(props.getExpirationMinutes(), ChronoUnit.MINUTES);
        String token = Jwts.builder()
                .subject(userId)
                .claim("email", email)
                .claim("role", role)   // read by vkp-jwt-rbac for /admin/** vs /customer/** enforcement
                .issuedAt(Date.from(now))
                .expiration(Date.from(expiresAt))
                .signWith(key())
                .compact();
        return new IssuedToken(token, expiresAt);
    }

    private SecretKey key() {
        return Keys.hmacShaKeyFor(props.getSecret().getBytes(StandardCharsets.UTF_8));
    }
}
