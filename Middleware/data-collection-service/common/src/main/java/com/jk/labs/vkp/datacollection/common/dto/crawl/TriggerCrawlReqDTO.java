package com.jk.labs.vkp.datacollection.common.dto.crawl;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TriggerCrawlReqDTO {

    /** Set by the controller from the path. */
    private String companyId;

    /** Crawl bounds (0 = DAG default: 1000 pages / depth 100). */
    private int maxPages;
    private int maxDepth;

    private String triggeredBy;
}
