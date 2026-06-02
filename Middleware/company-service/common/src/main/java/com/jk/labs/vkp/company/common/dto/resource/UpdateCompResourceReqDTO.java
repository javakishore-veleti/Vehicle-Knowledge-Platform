package com.jk.labs.vkp.company.common.dto.resource;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UpdateCompResourceReqDTO {

    @NotBlank
    private String companyId;

    @NotBlank
    private String resourceId;

    @Valid
    @NotNull
    private CompResourceDTO resource;
}
