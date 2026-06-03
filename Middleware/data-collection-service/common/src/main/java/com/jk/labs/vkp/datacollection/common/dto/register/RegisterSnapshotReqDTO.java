package com.jk.labs.vkp.datacollection.common.dto.register;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

/**
 * Register a company's filesystem-snapshot pages as {@code company_resource_graph} rows so each
 * page gets a stable PK ({@code resource_graph_id}) the admin UI can select for targeted indexing.
 */
@Data
@NoArgsConstructor
@AllArgsConstructor
public class RegisterSnapshotReqDTO {

    /** Graph FK (company UUID). Set by the controller from the path. */
    private String companyId;

    /** Snapshot folder name (company display name, e.g. {@code Toyota}). From the path. */
    private String company;

    /** Optional; defaults to {@code companyId} when absent. */
    private String companyResourceId;

    private String triggeredBy;
}
