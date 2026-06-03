package com.jk.labs.vkp.indexing.common.dto.admin;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class WorkflowDTO {

    private String wfId;
    private String name;
    private String wfType;
    private String targetRef;
    private String description;
    private String status;
}
