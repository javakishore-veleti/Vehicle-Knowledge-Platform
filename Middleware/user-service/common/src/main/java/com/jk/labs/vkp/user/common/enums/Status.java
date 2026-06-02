package com.jk.labs.vkp.user.common.enums;

/**
 * Lifecycle status applied to users and user resources.
 * Stored as a VARCHAR string in the data model (see README data architecture).
 */
public enum Status {
    ACTIVE,
    INACTIVE,
    DELETED;

    public static final String DEFAULT = ACTIVE.name();
}
