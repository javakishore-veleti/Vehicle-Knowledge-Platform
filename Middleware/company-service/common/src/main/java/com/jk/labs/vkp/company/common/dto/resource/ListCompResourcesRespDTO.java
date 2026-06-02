package com.jk.labs.vkp.company.common.dto.resource;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ListCompResourcesRespDTO {

    private List<CompResourceDTO> resources = new ArrayList<>();
    private long count;
}
