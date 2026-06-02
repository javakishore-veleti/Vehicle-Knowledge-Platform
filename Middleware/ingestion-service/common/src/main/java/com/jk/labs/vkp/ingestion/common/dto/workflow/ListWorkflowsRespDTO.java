package com.jk.labs.vkp.ingestion.common.dto.workflow;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ListWorkflowsRespDTO {

    private List<WorkflowRunDTO> runs = new ArrayList<>();
    private int count;
}
