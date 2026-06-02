package com.jk.labs.vkp.customer.common.dto.resource;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class DeleteCustResourceReqDTO {

    @NotBlank
    private String customerId;

    @NotBlank
    private String resourceId;
}
