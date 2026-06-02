package com.jk.labs.vkp.airflow.common.dto.list;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ListRunsReqDTO {

    private String dagId;

    /** Max runs to return (most recent first). */
    private int limit;
}
