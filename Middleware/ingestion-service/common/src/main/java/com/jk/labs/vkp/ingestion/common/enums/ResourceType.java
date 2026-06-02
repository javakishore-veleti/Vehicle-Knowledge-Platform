package com.jk.labs.vkp.ingestion.common.enums;

/**
 * Type of a ingestion resource. Mirrors the resource examples in the README
 * (Website, Blog, Documentation, Social Media, PDF, Video, Image Repository).
 * Stored as a VARCHAR string in the data model.
 */
public enum ResourceType {
    WEBSITE,
    BLOG,
    DOCUMENTATION,
    SOCIAL_MEDIA,
    PDF,
    VIDEO,
    IMAGE_REPOSITORY
}
