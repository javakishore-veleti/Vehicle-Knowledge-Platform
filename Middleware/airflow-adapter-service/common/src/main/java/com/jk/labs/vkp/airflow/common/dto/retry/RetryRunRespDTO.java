package com.jk.labs.vkp.airflow.common.dto.retry;

import com.jk.labs.vkp.airflow.common.dto.DagRunDTO;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class RetryRunRespDTO {

    private DagRunDTO dagRun;
}
