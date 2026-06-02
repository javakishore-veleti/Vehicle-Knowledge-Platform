package com.jk.labs.vkp.company.common.dto.resource;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ListCompResourcesReqDTO {

    @NotBlank
    private String companyId;
}
