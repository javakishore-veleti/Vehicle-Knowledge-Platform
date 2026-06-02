package com.jk.labs.vkp.user.common.error;

/**
 * Thrown when a requested user or user resource does not exist.
 * Mapped to HTTP 404 by the API layer's global exception handler.
 */
public class ResourceNotFoundException extends RuntimeException {

    public ResourceNotFoundException(String message) {
        super(message);
    }
}
