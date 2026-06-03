package com.jk.labs.vkp.indexing.dao.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.Instant;

/**
 * The indexing ledger (child of company_resource_graph). Blends the workflow + formula +
 * provider + vector-store target + status, so re-runs are idempotent and failures are
 * restartable. resource_graph_id is null for run-level rows, set for per-doc rows.
 */
@Entity
@Table(name = "resource_graph_index_log",
        indexes = @Index(name = "idx_rgil_company_id", columnList = "company_id"))
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ResourceGraphIndexLogEntity {

    @Id
    @Column(name = "index_log_id", length = 36, nullable = false, updatable = false)
    private String indexLogId;

    @Column(name = "company_id", length = 36, nullable = false)
    private String companyId;

    @Column(name = "resource_graph_id", length = 36)
    private String resourceGraphId;

    @Column(name = "wf_id", length = 36)
    private String wfId;
    @Column(name = "wf_type", length = 20)
    private String wfType;

    @Column(name = "index_formula_id", length = 36)
    private String indexFormulaId;
    @Column(name = "provider", length = 50)
    private String provider;
    @Column(name = "embedding_model", length = 100)
    private String embeddingModel;
    @Column(name = "indexed_to", length = 50)
    private String indexedTo;
    @Column(name = "provider_credential_id", length = 36)
    private String providerCredentialId;
    @Column(name = "vector_target", length = 150)
    private String vectorTarget;

    @Column(name = "scope", length = 20)
    private String scope;
    @Column(name = "doc_count")
    private Integer docCount;

    @Column(name = "status", length = 20)
    private String status;
    @Column(name = "version", length = 20)
    private String version;
    @Column(name = "run_ref", length = 150)
    private String runRef;
    @Column(name = "chunks")
    private Integer chunks;

    @Lob
    @Column(name = "error")
    private String error;

    @Column(name = "index_start_dt")
    private Instant indexStartDt;
    @Column(name = "index_end_dt")
    private Instant indexEndDt;
    @Column(name = "created_dt")
    private Instant createdDt;
    @Column(name = "updated_dt")
    private Instant updatedDt;
    @Column(name = "created_by", length = 50)
    private String createdBy;
    @Column(name = "updated_by", length = 50)
    private String updatedBy;
}
