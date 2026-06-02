package com.jk.labs.vkp.company.common.dto.resource;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class DeleteCompResourceReqDTO {

    @NotBlank
    private String companyId;

    @NotBlank
    private String resourceId;
}
