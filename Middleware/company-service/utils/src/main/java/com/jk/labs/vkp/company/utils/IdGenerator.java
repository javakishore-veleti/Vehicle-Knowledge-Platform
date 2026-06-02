package com.jk.labs.vkp.company.utils;

import lombok.AccessLevel;
import lombok.NoArgsConstructor;

import java.util.UUID;

/** Generates UUID-string identifiers, matching the VKP data model's id convention. */
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public final class IdGenerator {

    public static String newId() {
        return UUID.randomUUID().toString();
    }
}
