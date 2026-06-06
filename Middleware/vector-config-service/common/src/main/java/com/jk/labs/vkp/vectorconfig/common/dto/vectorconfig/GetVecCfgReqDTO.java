package com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GetVecCfgReqDTO {
    @NotBlank
    private String vectorConfigId;
}
