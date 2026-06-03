package com.jk.labs.vkp.indexing.dao.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Lob;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.Instant;

/** Reusable indexing configuration (embedding provider/model + chunking/params JSON). */
@Entity
@Table(name = "index_formula")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class IndexFormulaEntity {

    @Id
    @Column(name = "index_formula_id", length = 36, nullable = false, updatable = false)
    private String indexFormulaId;

    @Column(name = "name", length = 150, nullable = false)
    private String name;

    @Column(name = "embedding_provider", length = 50)
    private String embeddingProvider;

    @Column(name = "embedding_model", length = 100)
    private String embeddingModel;

    /** JSON: chunk_size, chunk_overlap, dim, temperature, top_p, ... */
    @Lob
    @Column(name = "params")
    private String params;

    @Column(name = "status", length = 15)
    private String status;

    @Column(name = "created_dt")
    private Instant createdDt;
    @Column(name = "updated_dt")
    private Instant updatedDt;
    @Column(name = "created_by", length = 50)
    private String createdBy;
    @Column(name = "updated_by", length = 50)
    private String updatedBy;
}
