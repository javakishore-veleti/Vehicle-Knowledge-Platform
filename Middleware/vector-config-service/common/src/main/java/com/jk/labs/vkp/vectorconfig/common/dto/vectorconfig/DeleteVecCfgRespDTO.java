package com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class DeleteVecCfgRespDTO {
    private String vectorConfigId;
    private boolean deleted;
}
