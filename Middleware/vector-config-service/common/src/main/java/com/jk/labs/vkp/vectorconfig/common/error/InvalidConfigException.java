package com.jk.labs.vkp.vectorconfig.common.error;

/**
 * Thrown when a vector configuration is structurally invalid (e.g. an unsupported
 * vector-store type). Mapped to HTTP 400 by the global exception handler.
 */
public class InvalidConfigException extends RuntimeException {
    public InvalidConfigException(String message) {
        super(message);
    }
}
