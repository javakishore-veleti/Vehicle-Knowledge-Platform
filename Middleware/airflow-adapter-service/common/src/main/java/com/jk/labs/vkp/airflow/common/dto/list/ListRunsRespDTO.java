package com.jk.labs.vkp.airflow.common.dto.list;

import com.jk.labs.vkp.airflow.common.dto.DagRunDTO;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ListRunsRespDTO {

    private List<DagRunDTO> runs = new ArrayList<>();
    private int count;
}
