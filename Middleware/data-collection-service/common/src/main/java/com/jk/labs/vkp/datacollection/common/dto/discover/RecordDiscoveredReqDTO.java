package com.jk.labs.vkp.datacollection.common.dto.discover;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

/** Callback payload: the discovery DAG reports the links it found for a graph root. */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RecordDiscoveredReqDTO {

    @NotBlank
    private String companyId;

    @NotBlank
    private String companyResourceId;

    /** The root (seed) graph node the discovered links are children of. */
    @NotBlank
    private String parentResourceGraphId;

    /** Final crawl status for the root, e.g. DISCOVERED or FAILED. */
    private String status;

    private List<String> links = new ArrayList<>();
}
