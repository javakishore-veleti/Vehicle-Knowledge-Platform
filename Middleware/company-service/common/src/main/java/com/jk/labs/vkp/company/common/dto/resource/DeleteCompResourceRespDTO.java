package com.jk.labs.vkp.company.common.dto.resource;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class DeleteCompResourceRespDTO {

    private String resourceId;
    private boolean deleted;
}
