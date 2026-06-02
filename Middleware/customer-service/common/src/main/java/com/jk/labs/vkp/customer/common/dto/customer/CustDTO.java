package com.jk.labs.vkp.customer.common.dto.customer;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

/**
 * Canonical wire shape of a customer. Field sizes mirror the README data model
 * (Company-style entity applied to Customer).
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class CustDTO {

    private String customerId;

    @NotBlank
    @Size(max = 100)
    private String name;

    @Size(max = 250)
    private String description;

    @Size(max = 15)
    private String status;

    private Instant createdDt;
    private Instant updatedDt;

    @Size(max = 50)
    private String createdBy;

    @Size(max = 50)
    private String updatedBy;
}
