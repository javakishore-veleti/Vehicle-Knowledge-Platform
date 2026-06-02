package com.jk.labs.vkp.ingestion.common.dto.content;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ListContentRespDTO {

    private List<ContentDTO> items = new ArrayList<>();
    private int count;
}
