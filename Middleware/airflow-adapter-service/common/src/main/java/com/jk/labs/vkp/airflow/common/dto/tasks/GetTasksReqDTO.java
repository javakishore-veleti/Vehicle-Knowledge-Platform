package com.jk.labs.vkp.airflow.common.dto.tasks;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GetTasksReqDTO {

    private String dagId;
    private String runId;
}
