package com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

/**
 * Canonical wire shape of a vector configuration. Determines where a company resource's
 * content is indexed. Field sizes mirror the README {@code company_resource_vector_config}
 * data model.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class VecCfgDTO {

    private String vectorConfigId;

    @Size(max = 36)
    private String companyId;

    @Size(max = 36)
    private String companyResourceId;

    /** One of VectorStoreType (mongodb, chromadb, pgvector, weaviate, pinecone). */
    @NotBlank
    @Size(max = 50)
    private String vectorStoreType;

    @Size(max = 100)
    private String vectorStoreName;

    @Size(max = 100)
    private String collectionName;

    @Size(max = 100)
    private String indexName;

    @Size(max = 100)
    private String embeddingModel;

    /** When true, this is the primary store for the resource (at most one per resource). */
    private Boolean isPrimary;

    @Size(max = 15)
    private String status;

    /** Free-form provider-specific settings, serialized as JSON text. */
    private String addlData;

    private Instant createdDt;
    private Instant updatedDt;

    @Size(max = 50)
    private String createdBy;

    @Size(max = 50)
    private String updatedBy;
}
