package com.jk.labs.vkp.airflow.common.dto.run;

import com.jk.labs.vkp.airflow.common.dto.DagRunDTO;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GetRunRespDTO {

    private DagRunDTO dagRun;
}
