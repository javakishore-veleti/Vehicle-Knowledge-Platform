package com.jk.labs.vkp.datacollection.common.dto.graph;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

/** A node in the company_resource_graph (a discovered URL). */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ResourceGraphNodeDTO {

    private String resourceGraphId;
    private String companyId;
    private String companyResourceId;
    private String parentResourceGraphId;
    private String resourceUrl;
    private String resourceType;
    private String parentResourceType;
    private String crawlStatus;
    private String status;
    private Instant createdDt;
    private Instant updatedDt;
}
