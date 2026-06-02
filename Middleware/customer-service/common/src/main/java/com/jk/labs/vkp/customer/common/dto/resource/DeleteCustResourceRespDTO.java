package com.jk.labs.vkp.customer.common.dto.resource;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class DeleteCustResourceRespDTO {

    private String resourceId;
    private boolean deleted;
}
