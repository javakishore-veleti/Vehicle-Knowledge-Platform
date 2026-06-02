package com.jk.labs.vkp.datacollection.common.dto.graph;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GetGraphReqDTO {

    @NotBlank
    private String companyId;
}
