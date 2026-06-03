package com.jk.labs.vkp.indexing.common.enums;

/**
 * Lifecycle status applied to companies and indexing resources.
 * Stored as a VARCHAR string in the data model (see README data architecture).
 */
public enum Status {
    ACTIVE,
    INACTIVE,
    DELETED;

    public static final String DEFAULT = ACTIVE.name();
}
