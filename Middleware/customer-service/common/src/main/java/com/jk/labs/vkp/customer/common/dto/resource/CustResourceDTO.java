package com.jk.labs.vkp.customer.common.dto.resource;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

/**
 * Canonical wire shape of a customer resource (a related table of customer).
 * Field sizes mirror the README "Company Resource" data model applied to Customer.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CustResourceDTO {

    private String customerResourceId;

    private String customerId;

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
