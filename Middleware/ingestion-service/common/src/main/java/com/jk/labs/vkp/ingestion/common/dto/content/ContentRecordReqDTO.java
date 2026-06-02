package com.jk.labs.vkp.ingestion.common.dto.content;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

/** Callback payload: the ingestion DAG reports the content it extracted. */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ContentRecordReqDTO {

    @NotBlank
    private String companyId;

    @NotBlank
    private String companyResourceId;

    private List<ContentItemDTO> items = new ArrayList<>();
}
