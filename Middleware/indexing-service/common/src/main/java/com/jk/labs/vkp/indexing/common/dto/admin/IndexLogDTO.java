package com.jk.labs.vkp.indexing.common.dto.admin;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class IndexLogDTO {

    private String indexLogId;
    private String companyId;
    private String resourceGraphId;
    private String wfId;
    private String wfType;
    private String indexFormulaId;
    private String provider;
    private String embeddingModel;
    private String indexedTo;
    private String vectorTarget;
    private String scope;
    private Integer docCount;
    private String status;
    private String version;
    private String runRef;
    private Integer chunks;
    private String error;
    private Instant indexStartDt;
    private Instant indexEndDt;
    private Instant createdDt;
    private Instant updatedDt;
}
