package com.jk.labs.vkp.customer.common.dto.customer;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ListCustsReqDTO {

    /** Optional status filter (e.g. ACTIVE). When null, all customers are returned. */
    private String status;
}
