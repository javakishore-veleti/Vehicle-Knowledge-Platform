package com.jk.labs.vkp.datacollection.common.dto.workflow;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ListWorkflowsReqDTO {

    private String dagId;
}
