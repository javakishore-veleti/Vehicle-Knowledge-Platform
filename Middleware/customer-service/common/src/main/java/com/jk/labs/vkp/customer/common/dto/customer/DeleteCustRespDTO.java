package com.jk.labs.vkp.customer.common.dto.customer;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class DeleteCustRespDTO {

    private String customerId;
    private boolean deleted;
}
