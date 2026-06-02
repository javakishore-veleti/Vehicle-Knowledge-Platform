package com.jk.labs.vkp.ingestion.common.dto.content;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

/** A stored extracted-content row (company_resource_content), without the full text body. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ContentDTO {

    private String contentId;
    private String companyId;
    private String companyResourceId;
    private String resourceGraphId;
    private String sourceUrl;
    private String title;
    private String contentHash;
    private Integer textLength;
    private String crawlStatus;
    private String embeddingStatus;
    private Instant createdDt;
    private Instant updatedDt;
}
