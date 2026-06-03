package com.jk.labs.vkp.datacollection.common.dto.snapshot;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

/** One crawled page element from a snapshot's crawl-*.json. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SnapshotPageDTO {

    private String url;
    private int depth;
    private String title;
    private String text;          // truncated for the list view
    private int textLength;       // full length
    @lombok.Builder.Default
    private List<SnapshotImageRefDTO> images = new java.util.ArrayList<>();
    private int linksCount;
    private String fetchedAt;
}
