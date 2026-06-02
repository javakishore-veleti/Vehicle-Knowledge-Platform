package com.jk.labs.vkp.ingestion.common.dto.workflow;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

/** A workflow (Airflow DAG) run, as shown in the admin portal's Workflows list. */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class WorkflowRunDTO {

    private String dagId;
    private String dagRunId;
    private String state;
    private String startDate;
    private String endDate;
}
