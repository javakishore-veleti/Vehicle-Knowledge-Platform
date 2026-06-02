package com.jk.labs.vkp.customer.common.enums;

/**
 * Lifecycle status applied to customers and customer resources.
 * Stored as a VARCHAR string in the data model (see README data architecture).
 */
public enum Status {
    ACTIVE,
    INACTIVE,
    DELETED;

    public static final String DEFAULT = ACTIVE.name();
}
