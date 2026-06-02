package com.jk.labs.vkp.ingestion.common.dto.content;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** A single extracted-content item reported by the ingestion DAG. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class ContentItemDTO {

    private String resourceGraphId;
    private String sourceUrl;
    private String title;
    private String cleanText;
    private String contentHash;
}
