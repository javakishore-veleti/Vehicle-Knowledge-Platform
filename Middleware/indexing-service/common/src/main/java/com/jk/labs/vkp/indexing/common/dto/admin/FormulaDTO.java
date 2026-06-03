package com.jk.labs.vkp.indexing.common.dto.admin;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class FormulaDTO {

    private String indexFormulaId;
    private String name;
    private String embeddingProvider;
    private String embeddingModel;
    private String params;
    private String status;
}
