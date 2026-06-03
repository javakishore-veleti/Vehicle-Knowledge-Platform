package com.jk.labs.vkp.indexing.common.dto.trigger;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class TriggerIndexRespDTO {

    private String indexLogId;
    private String wfType;
    private String status;
    private String runRef;
    private boolean deduped;   // true = an equivalent run already existed, this was skipped
    private String message;
}
