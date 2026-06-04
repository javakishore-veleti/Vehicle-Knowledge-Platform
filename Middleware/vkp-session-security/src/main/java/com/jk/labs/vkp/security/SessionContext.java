package com.jk.labs.vkp.security;

import com.fasterxml.jackson.annotation.JsonIgnoreProperties;

/** The decrypted session payload threaded through a request (carried inside the encrypted token). */
@JsonIgnoreProperties(ignoreUnknown = true)
public record SessionContext(String sessionId, UserType userType, String userId, long issuedAt) {

    public static SessionContext guest(String sessionId) {
        return new SessionContext(sessionId, UserType.GUEST, null, System.currentTimeMillis());
    }

    public static SessionContext auth(String sessionId, String userId) {
        return new SessionContext(sessionId, UserType.AUTH, userId, System.currentTimeMillis());
    }

    public boolean isAuthenticated() {
        return userType == UserType.AUTH;
    }
}
