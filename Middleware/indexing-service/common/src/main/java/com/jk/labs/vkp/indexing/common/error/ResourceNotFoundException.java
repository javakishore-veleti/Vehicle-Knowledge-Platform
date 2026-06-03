package com.jk.labs.vkp.indexing.common.error;

/**
 * Thrown when a requested indexing or indexing resource does not exist.
 * Mapped to HTTP 404 by the API layer's global exception handler.
 */
public class ResourceNotFoundException extends RuntimeException {

    public ResourceNotFoundException(String message) {
        super(message);
    }
}
