package com.jk.labs.vkp.indexing.common.dto.callback;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/** Executor (Spring-AI wfs-java or Airflow DAG) reports progress/terminal state for a log. */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class IndexCallbackReqDTO {

    /** Set by the controller from the path. */
    private String indexLogId;

    @NotBlank
    private String status;   // IN_PROGRESS | INDEXED | FAILED

    private Integer chunks;
    private String error;
    private String runRef;
}
