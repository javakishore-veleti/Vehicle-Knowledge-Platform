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

    /** Optional server-side pagination. When limit is null/0 the full graph is returned. */
    private Integer offset;
    private Integer limit;

    public GetGraphReqDTO(String companyId) {
        this.companyId = companyId;
    }
}
