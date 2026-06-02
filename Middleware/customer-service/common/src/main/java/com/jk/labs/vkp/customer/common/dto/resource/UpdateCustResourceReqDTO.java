package com.jk.labs.vkp.customer.common.dto.resource;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UpdateCustResourceReqDTO {

    @NotBlank
    private String customerId;

    @NotBlank
    private String resourceId;

    @Valid
    @NotNull
    private CustResourceDTO resource;
}
