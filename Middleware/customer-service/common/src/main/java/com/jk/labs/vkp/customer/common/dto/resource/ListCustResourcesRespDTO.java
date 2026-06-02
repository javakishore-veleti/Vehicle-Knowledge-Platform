package com.jk.labs.vkp.customer.common.dto.resource;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ListCustResourcesRespDTO {

    private List<CustResourceDTO> resources = new ArrayList<>();
    private long count;
}
