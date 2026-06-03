package com.jk.labs.vkp.indexing.common.dto.trigger;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

/** Trigger an indexing run for a company via the selected workflow + formula. */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class TriggerIndexReqDTO {

    /** Set by the controller from the path. */
    private String companyId;

    /** Company name = the snapshot folder the executor/DAG reads. Provided by the portal. */
    private String companyName;

    @NotBlank
    private String wfId;

    @NotBlank
    private String indexFormulaId;

    /** Optional override; otherwise resolved from the formula's provider + a default vector store. */
    private String providerCredentialId;

    /** 1..10000 selected doc (resource_graph) ids; empty/null = whole company. */
    private List<String> docIds;

    /** Re-run even if an equivalent run already exists. */
    private boolean force;

    private String triggeredBy;
}
