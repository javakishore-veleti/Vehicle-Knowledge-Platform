package com.jk.labs.vkp.user.common.error;

/** Thrown on failed authentication (bad credentials / invalid or expired token). Maps to 401. */
public class UnauthorizedException extends RuntimeException {

    public UnauthorizedException(String message) {
        super(message);
    }
}
