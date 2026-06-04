package com.jk.labs.vkp.security;

/** Whether a session belongs to a guest or an authenticated user (drives guest vs auth query tables). */
public enum UserType {
    GUEST,
    AUTH
}
