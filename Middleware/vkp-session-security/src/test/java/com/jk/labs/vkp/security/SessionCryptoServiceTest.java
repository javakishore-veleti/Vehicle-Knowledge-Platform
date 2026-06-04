package com.jk.labs.vkp.security;

import org.junit.jupiter.api.Test;

import java.util.Base64;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;

class SessionCryptoServiceTest {

    private final SessionCryptoService crypto =
            new SessionCryptoService(Base64.getEncoder().encodeToString(new byte[32]));

    @Test
    void textRoundTrips() {
        String token = crypto.encrypt("hello-123");
        assertNotEquals("hello-123", token);          // opaque
        assertEquals("hello-123", crypto.decrypt(token));
    }

    @Test
    void contextRoundTrips() {
        String token = crypto.issue(SessionContext.auth("ses_1", "user_9"));
        SessionContext back = crypto.parse(token);
        assertEquals("ses_1", back.sessionId());
        assertEquals(UserType.AUTH, back.userType());
        assertEquals("user_9", back.userId());
        assertTrue(back.isAuthenticated());
    }

    @Test
    void guestContext() {
        SessionContext g = crypto.parse(crypto.issue(SessionContext.guest("ses_g")));
        assertEquals(UserType.GUEST, g.userType());
        assertFalse(g.isAuthenticated());
    }

    @Test
    void sameInputProducesDifferentTokens() {
        assertNotEquals(crypto.encrypt("same"), crypto.encrypt("same"));   // random IV
    }

    @Test
    void tamperedTokenIsRejected() {
        String token = crypto.encrypt("x");
        assertThrows(SessionCryptoException.class, () -> crypto.decrypt(token + "AB"));
    }

    @Test
    void wrongKeyCannotDecrypt() {
        byte[] other = new byte[32];
        other[0] = 1;
        SessionCryptoService stranger = new SessionCryptoService(Base64.getEncoder().encodeToString(other));
        String token = crypto.encrypt("secret");
        assertThrows(SessionCryptoException.class, () -> stranger.decrypt(token));
    }
}
