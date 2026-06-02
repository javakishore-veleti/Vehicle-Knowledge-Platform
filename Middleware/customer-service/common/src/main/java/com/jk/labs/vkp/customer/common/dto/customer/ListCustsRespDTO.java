package com.jk.labs.vkp.customer.common.dto.customer;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ListCustsRespDTO {

    private List<CustDTO> customers = new ArrayList<>();
    private long count;
}
