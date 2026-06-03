package com.jk.labs.vkp.datacollection.common.dto.snapshot;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ListPagesReqDTO {

    @NotBlank
    private String company;
    private int offset;
    private int limit;

    /** When true, return full page text (for indexing) instead of the truncated list-view preview. */
    private boolean full;
}
