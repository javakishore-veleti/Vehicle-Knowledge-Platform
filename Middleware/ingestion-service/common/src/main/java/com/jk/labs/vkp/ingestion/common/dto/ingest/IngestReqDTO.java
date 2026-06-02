package com.jk.labs.vkp.ingestion.common.dto.ingest;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class IngestReqDTO {

    /** Set by the controller from the path. */
    private String companyId;

    /** Set by the controller from the path. */
    private String companyResourceId;

    /** Max discovered links to crawl in this run (0 = service default). */
    private int limit;

    private String triggeredBy;
}
