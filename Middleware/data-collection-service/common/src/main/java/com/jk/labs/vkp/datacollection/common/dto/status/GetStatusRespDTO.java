package com.jk.labs.vkp.datacollection.common.dto.status;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GetStatusRespDTO {

    private String dagId;
    private String dagRunId;
    private String state;
}
