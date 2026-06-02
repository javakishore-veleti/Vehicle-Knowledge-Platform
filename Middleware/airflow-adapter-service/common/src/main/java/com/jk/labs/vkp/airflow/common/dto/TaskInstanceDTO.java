package com.jk.labs.vkp.airflow.common.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** Normalized view of an Airflow task instance. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TaskInstanceDTO {

    private String taskId;
    private String state;
    private Integer tryNumber;
    private String startDate;
    private String endDate;
}
