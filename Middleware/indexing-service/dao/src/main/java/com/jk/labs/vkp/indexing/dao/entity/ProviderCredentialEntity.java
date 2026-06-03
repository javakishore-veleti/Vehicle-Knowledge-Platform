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

/** Credentials/config for a provider (embedding or vector store). Many per type allowed. */
@Entity
@Table(name = "provider_credentials")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ProviderCredentialEntity {

    @Id
    @Column(name = "provider_credential_id", length = 36, nullable = false, updatable = false)
    private String providerCredentialId;

    /** sentence-transformers | openai | pgvector | mongodb-vector | pinecone | weaviate | chroma | opensearch | ... */
    @Column(name = "provider_type", length = 50, nullable = false)
    private String providerType;

    @Column(name = "name", length = 150, nullable = false)
    private String name;

    /** JSON: endpoint/region/index/keys (secrets). */
    @Lob
    @Column(name = "config")
    private String config;

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
