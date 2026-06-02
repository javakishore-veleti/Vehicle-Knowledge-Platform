package com.jk.labs.vkp.company.common.dto.resource;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

/**
 * Canonical wire shape of a company resource (a related table of company).
 * Field sizes mirror the README "Company Resource" data model applied to Company.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CompResourceDTO {

    private String companyResourceId;

    private String companyId;

    @NotBlank
    @Size(max = 150)
    private String resourceName;

    @NotBlank
    @Size(max = 1000)
    private String resourceLink;

    @Size(max = 50)
    private String resourceType;

    @Size(max = 15)
    private String status;

    private Instant createdDt;
    private Instant updatedDt;

    @Size(max = 50)
    private String createdBy;

    @Size(max = 50)
    private String updatedBy;
}
