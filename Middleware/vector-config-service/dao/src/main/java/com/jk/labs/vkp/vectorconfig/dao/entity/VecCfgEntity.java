package com.jk.labs.vkp.vectorconfig.dao.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.Instant;

/** JPA entity for the {@code company_resource_vector_config} table (h2 / postgres profiles). */
@Entity
@Table(name = "company_resource_vector_config")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class VecCfgEntity {

    @Id
    @Column(name = "vector_config_id", length = 36, nullable = false, updatable = false)
    private String vectorConfigId;

    @Column(name = "company_id", length = 36)
    private String companyId;

    @Column(name = "company_resource_id", length = 36)
    private String companyResourceId;

    @Column(name = "vector_store_type", length = 50, nullable = false)
    private String vectorStoreType;

    @Column(name = "vector_store_name", length = 100)
    private String vectorStoreName;

    @Column(name = "collection_name", length = 100)
    private String collectionName;

    @Column(name = "index_name", length = 100)
    private String indexName;

    @Column(name = "embedding_model", length = 100)
    private String embeddingModel;

    @Column(name = "is_primary")
    private Boolean isPrimary;

    @Column(name = "status", length = 15)
    private String status;

    @Column(name = "addl_data")
    private String addlData;

    @Column(name = "created_dt")
    private Instant createdDt;

    @Column(name = "updated_dt")
    private Instant updatedDt;

    @Column(name = "created_by", length = 50)
    private String createdBy;

    @Column(name = "updated_by", length = 50)
    private String updatedBy;
}
