package com.jk.labs.vkp.indexing.common.dto.callback;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class IndexCallbackRespDTO {

    private String indexLogId;
    private String status;
}
