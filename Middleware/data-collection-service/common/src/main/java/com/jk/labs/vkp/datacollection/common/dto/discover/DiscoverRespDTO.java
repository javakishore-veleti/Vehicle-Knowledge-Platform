package com.jk.labs.vkp.datacollection.common.dto.discover;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class DiscoverRespDTO {

    private String rootResourceGraphId;
    private String dagId;
    private String dagRunId;
    private String state;
}
