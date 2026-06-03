package com.jk.labs.vkp.datacollection.common.dto.register;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** Outcome of registering snapshot pages as graph rows. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class RegisterSnapshotRespDTO {

    /** New graph rows created this call. */
    private int registered;

    /** Pages already registered (skipped, idempotent). */
    private int skipped;

    /** Total snapshot pages seen. */
    private int total;
}
