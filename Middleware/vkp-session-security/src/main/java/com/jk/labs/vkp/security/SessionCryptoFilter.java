package com.jk.labs.vkp.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;
import lombok.extern.slf4j.Slf4j;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;
import java.util.HashSet;
import java.util.Set;

/**
 * Reads the encrypted session token from the configured header (or param), decrypts it into a
 * {@link SessionContext} exposed via {@link SessionContextHolder} + the request attribute
 * {@code vkp.session}, and wraps the request so configured encrypted params are decrypted for
 * controllers. Optionally enforces presence of a valid token (401).
 */
@Slf4j
public class SessionCryptoFilter extends OncePerRequestFilter {

    public static final String ATTR = "vkp.session";

    private final SessionCryptoService crypto;
    private final SessionSecurityProperties props;
    private final Set<String> encryptedParams;

    public SessionCryptoFilter(SessionCryptoService crypto, SessionSecurityProperties props) {
        this.crypto = crypto;
        this.props = props;
        this.encryptedParams = new HashSet<>(props.getEncryptedParams());
    }

    @Override
    protected void doFilterInternal(HttpServletRequest req, HttpServletResponse res, FilterChain chain)
            throws ServletException, IOException {
        String token = req.getHeader(props.getHeader());
        if (token == null || token.isBlank()) {
            token = req.getParameter(props.getParam());
        }

        SessionContext ctx = null;
        if (token != null && !token.isBlank()) {
            try {
                ctx = crypto.parse(token);
            } catch (RuntimeException e) {
                log.debug("Invalid session token: {}", e.getMessage());
            }
        }

        if (ctx == null && props.isRequired()) {
            res.sendError(HttpServletResponse.SC_UNAUTHORIZED, "Missing or invalid session token");
            return;
        }

        try {
            if (ctx != null) {
                SessionContextHolder.set(ctx);
                req.setAttribute(ATTR, ctx);
            }
            HttpServletRequest effective = encryptedParams.isEmpty()
                    ? req : new DecryptingRequestWrapper(req, crypto, encryptedParams);
            chain.doFilter(effective, res);
        } finally {
            SessionContextHolder.clear();
        }
    }
}
