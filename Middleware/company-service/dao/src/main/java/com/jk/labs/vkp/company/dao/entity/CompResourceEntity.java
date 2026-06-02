package com.jk.labs.vkp.company.dao.entity;

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

/** JPA entity for the {@code company_resources} table (h2 / postgres profiles). */
@Entity
@Table(name = "company_resources",
        indexes = @Index(name = "idx_company_resources_company_id", columnList = "company_id"))
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CompResourceEntity {

    @Id
    @Column(name = "company_resource_id", length = 36, nullable = false, updatable = false)
    private String companyResourceId;

    @Column(name = "company_id", length = 36, nullable = false)
    private String companyId;

    @Column(name = "resource_name", length = 150, nullable = false)
    private String resourceName;

    @Column(name = "resource_link", length = 1000, nullable = false)
    private String resourceLink;

    @Column(name = "resource_type", length = 50)
    private String resourceType;

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
