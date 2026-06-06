package com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Filters for listing vector configs. Any field may be null. When companyResourceId is
 * set, configs for that resource are returned; else filtered by companyId and/or status.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ListVecCfgsReqDTO {
    private String companyResourceId;
    private String companyId;
    private String status;
}
