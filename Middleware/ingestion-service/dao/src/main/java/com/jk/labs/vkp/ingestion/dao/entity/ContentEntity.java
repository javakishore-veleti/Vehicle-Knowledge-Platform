package com.jk.labs.vkp.ingestion.dao.entity;

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

/** JPA entity for the {@code company_resource_content} table (h2 / postgres profiles). */
@Entity
@Table(name = "company_resource_content",
        indexes = @Index(name = "idx_company_resource_content_company_id", columnList = "company_id"))
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ContentEntity {

    @Id
    @Column(name = "content_id", length = 36, nullable = false, updatable = false)
    private String contentId;

    @Column(name = "company_id", length = 36, nullable = false)
    private String companyId;

    @Column(name = "company_resource_id", length = 36, nullable = false)
    private String companyResourceId;

    @Column(name = "resource_graph_id", length = 36)
    private String resourceGraphId;

    @Column(name = "source_url", length = 1000, nullable = false)
    private String sourceUrl;

    @Column(name = "title", length = 250)
    private String title;

    @Lob
    @Column(name = "clean_text")
    private String cleanText;

    @Column(name = "content_hash", length = 128)
    private String contentHash;

    @Column(name = "embedding_status", length = 30)
    private String embeddingStatus;

    @Column(name = "crawl_status", length = 30)
    private String crawlStatus;

    @Column(name = "created_dt")
    private Instant createdDt;

    @Column(name = "updated_dt")
    private Instant updatedDt;

    @Column(name = "created_by", length = 50)
    private String createdBy;

    @Column(name = "updated_by", length = 50)
    private String updatedBy;
}
