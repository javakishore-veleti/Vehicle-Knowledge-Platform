package com.jk.labs.vkp.airflow.common.dto.retry;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class RetryRunReqDTO {

    private String dagId;
    private String runId;
}
