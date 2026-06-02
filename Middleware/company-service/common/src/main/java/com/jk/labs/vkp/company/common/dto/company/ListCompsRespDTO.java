package com.jk.labs.vkp.company.common.dto.company;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ListCompsRespDTO {

    private List<CompDTO> companies = new ArrayList<>();
    private long count;
}
