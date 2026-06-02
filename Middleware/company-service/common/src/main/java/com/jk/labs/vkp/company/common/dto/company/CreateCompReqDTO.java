package com.jk.labs.vkp.company.common.dto.company;

import jakarta.validation.Valid;
import jakarta.validation.constraints.NotNull;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class CreateCompReqDTO {

    @Valid
    @NotNull
    private CompDTO company;
}
