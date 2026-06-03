package com.jk.labs.vkp.datacollection.common.dto.snapshot;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** Summary of one company's crawl snapshot on disk. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SnapshotCompanyDTO {

    private String company;
    private boolean completed;   // has a __COMPLETED__ marker
    private int pages;
    private int files;
    private int images;
    private String completedAt;
}
