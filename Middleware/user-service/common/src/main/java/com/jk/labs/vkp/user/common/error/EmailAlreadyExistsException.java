package com.jk.labs.vkp.user.common.error;

/** Thrown when signing up with an email that already exists. Maps to 409. */
public class EmailAlreadyExistsException extends RuntimeException {

    public EmailAlreadyExistsException(String message) {
        super(message);
    }
}
