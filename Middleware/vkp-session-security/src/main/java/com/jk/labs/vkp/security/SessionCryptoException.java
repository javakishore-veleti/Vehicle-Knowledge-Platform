package com.jk.labs.vkp.security;

/** Thrown when a session token / encrypted parameter cannot be produced or read. */
public class SessionCryptoException extends RuntimeException {

    public SessionCryptoException(String message) {
        super(message);
    }

    public SessionCryptoException(String message, Throwable cause) {
        super(message, cause);
    }
}
