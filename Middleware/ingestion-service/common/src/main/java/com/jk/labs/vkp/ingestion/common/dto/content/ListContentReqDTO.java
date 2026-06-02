package com.jk.labs.vkp.ingestion.common.dto.content;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ListContentReqDTO {

    @NotBlank
    private String companyId;
}
