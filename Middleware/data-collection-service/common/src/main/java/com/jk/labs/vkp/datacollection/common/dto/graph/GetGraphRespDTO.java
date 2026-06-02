package com.jk.labs.vkp.datacollection.common.dto.graph;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GetGraphRespDTO {

    private List<ResourceGraphNodeDTO> nodes = new ArrayList<>();
    private int count;
}
