package com.jk.labs.vkp.ingestion.common.dto.status;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GetStatusReqDTO {

    private String dagId;
    private String runId;
}
