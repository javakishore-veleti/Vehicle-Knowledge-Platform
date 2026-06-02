package com.jk.labs.vkp.ingestion.common.dto.ingest;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class IngestRespDTO {

    private String dagId;
    private String dagRunId;
    private String state;
}
