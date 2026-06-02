package com.jk.labs.vkp.company.common.dto.company;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ListCompsReqDTO {

    /** Optional status filter (e.g. ACTIVE). When null, all companies are returned. */
    private String status;
}
