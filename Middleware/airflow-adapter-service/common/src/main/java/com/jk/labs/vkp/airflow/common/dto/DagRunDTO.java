package com.jk.labs.vkp.airflow.common.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

/** Normalized view of an Airflow DAG run (a subset of Airflow's dagRun object). */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DagRunDTO {

    private String dagId;
    private String dagRunId;
    private String state;
    private String logicalDate;
    private String startDate;
    private String endDate;
    private Map<String, Object> conf;
    private String note;
}
