package com.jk.labs.vkp.datacollection.common.dto.discover;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class DiscoverReqDTO {

    /** Set by the controller from the path. */
    private String companyId;

    /** Set by the controller from the path. */
    private String companyResourceId;

    @NotBlank
    private String seedUrl;

    private String resourceType;

    private String triggeredBy;
}
