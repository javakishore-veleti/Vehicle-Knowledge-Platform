package com.jk.labs.vkp.airflow.common.dto.cancel;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CancelRunReqDTO {

    private String dagId;
    private String runId;
}
