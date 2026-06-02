package com.jk.labs.vkp.airflow.common.dto.trigger;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.Map;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TriggerDagReqDTO {

    /** Set by the controller from the path. */
    private String dagId;

    /** DAG run configuration passed through to Airflow as {@code conf}. */
    private Map<String, Object> conf;

    /** Optional free-text note recorded on the run. */
    private String note;

    /** Optional actor that requested the run (for traceability). */
    private String triggeredBy;

    /** Optional run type tag (e.g. ON_DEMAND, SCHEDULED). */
    private String runType;
}
