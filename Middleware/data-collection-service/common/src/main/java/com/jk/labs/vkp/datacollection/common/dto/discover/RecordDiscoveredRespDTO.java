package com.jk.labs.vkp.datacollection.common.dto.discover;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class RecordDiscoveredRespDTO {

    private int added;
    private String parentResourceGraphId;
}
