package com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CreateVecCfgReqDTO {

    @NotBlank
    private String companyResourceId;

    @Valid
    @NotNull
    private VecCfgDTO vectorConfig;
}
