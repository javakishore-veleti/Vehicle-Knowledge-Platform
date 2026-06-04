package com.jk.labs.vkp.user.api.controller;

import com.jk.labs.vkp.security.Ids;
import com.jk.labs.vkp.security.SessionContext;
import com.jk.labs.vkp.security.SessionContextHolder;
import com.jk.labs.vkp.security.SessionCryptoService;
import com.jk.labs.vkp.user.common.api.ApiRoutes;
import lombok.RequiredArgsConstructor;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.LinkedHashMap;
import java.util.Map;

/**
 * Mints the encrypted session token the UI carries on every API call (from vkp-session-security),
 * and a whoami endpoint that proves the shared filter decrypted it back into a {@link SessionContext}.
 */
@RestController
@RequestMapping(ApiRoutes.SESSION)
@RequiredArgsConstructor
public class SessionController {

    private final SessionCryptoService crypto;

    /** Anonymous/guest session — a fresh session id encrypted into an opaque token for the UI. */
    @PostMapping("/guest")
    public Map<String, Object> guest() {
        SessionContext ctx = SessionContext.guest(Ids.newSessionId());
        return token(ctx);
    }

    /** Authenticated session — normally minted at signin once credentials are verified. */
    @PostMapping("/auth/{userId}")
    public Map<String, Object> auth(@PathVariable String userId) {
        SessionContext ctx = SessionContext.auth(Ids.newSessionId(), userId);
        return token(ctx);
    }

    /** Echoes the decrypted context for the X-VKP-Session token (set by the shared filter). */
    @GetMapping("/whoami")
    public Map<String, Object> whoami() {
        SessionContext ctx = SessionContextHolder.get();
        Map<String, Object> out = new LinkedHashMap<>();
        if (ctx == null) {
            out.put("authenticated", false);
            out.put("message", "no/invalid session token");
            return out;
        }
        out.put("sessionId", ctx.sessionId());
        out.put("userType", ctx.userType());
        out.put("userId", ctx.userId());
        out.put("authenticated", ctx.isAuthenticated());
        return out;
    }

    private Map<String, Object> token(SessionContext ctx) {
        Map<String, Object> out = new LinkedHashMap<>();
        out.put("sessionId", ctx.sessionId());
        out.put("userType", ctx.userType());
        out.put("userId", ctx.userId());
        out.put("token", crypto.issue(ctx));   // opaque AES-256-GCM token; send on X-VKP-Session
        return out;
    }
}
