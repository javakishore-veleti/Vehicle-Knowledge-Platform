package com.jk.labs.vkp.customer.common.dto.customer;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UpdateCustReqDTO {

    @NotBlank
    private String customerId;

    @Valid
    @NotNull
    private CustDTO customer;
}
