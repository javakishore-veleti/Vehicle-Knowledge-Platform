package com.jk.labs.vkp.airflow.common.dto.run;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GetRunReqDTO {

    private String dagId;
    private String runId;
}
