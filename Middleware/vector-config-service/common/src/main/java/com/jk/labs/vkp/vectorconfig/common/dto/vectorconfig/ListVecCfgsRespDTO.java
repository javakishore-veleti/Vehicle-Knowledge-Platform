package com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ListVecCfgsRespDTO {
    private List<VecCfgDTO> vectorConfigs = new ArrayList<>();
    private long count;
}
