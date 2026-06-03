package com.jk.labs.vkp.datacollection.common.dto.crawl;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TriggerCrawlRespDTO {

    private String dagId;
    private String dagRunId;
    private String state;
}
