package com.jk.labs.vkp.airflow.common.dto.cancel;

import com.jk.labs.vkp.airflow.common.dto.DagRunDTO;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CancelRunRespDTO {

    private DagRunDTO dagRun;
}
