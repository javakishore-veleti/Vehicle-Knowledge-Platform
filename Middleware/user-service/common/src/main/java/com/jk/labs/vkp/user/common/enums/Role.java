package com.jk.labs.vkp.user.common.enums;

/** Role of a portal end-user. Stored as a VARCHAR string. */
public enum Role {
    USER,
    ADMIN;

    public static final String DEFAULT = USER.name();
}
