package com.jk.labs.vkp.datacollection.dao.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Index;
import jakarta.persistence.Table;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;
import lombok.Setter;

import java.time.Instant;

/** JPA entity for the {@code company_resource_graph} table (h2 / postgres profiles). */
@Entity
@Table(name = "company_resource_graph",
        indexes = @Index(name = "idx_company_resource_graph_company_id", columnList = "company_id"))
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ResourceGraphNodeEntity {

    @Id
    @Column(name = "resource_graph_id", length = 36, nullable = false, updatable = false)
    private String resourceGraphId;

    @Column(name = "company_id", length = 36, nullable = false)
    private String companyId;

    @Column(name = "company_resource_id", length = 36, nullable = false)
    private String companyResourceId;

    @Column(name = "parent_resource_graph_id", length = 36)
    private String parentResourceGraphId;

    @Column(name = "resource_url", length = 1000, nullable = false)
    private String resourceUrl;

    @Column(name = "resource_type", length = 50)
    private String resourceType;

    @Column(name = "parent_resource_type", length = 50)
    private String parentResourceType;

    @Column(name = "crawl_status", length = 30)
    private String crawlStatus;

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
