package com.jk.labs.vkp.vectorconfig.common.enums;

/** Lifecycle status applied to a vector configuration. Stored as a VARCHAR string. */
public enum Status {
    ACTIVE,
    INACTIVE,
    DELETED;

    public static final String DEFAULT = ACTIVE.name();
}
