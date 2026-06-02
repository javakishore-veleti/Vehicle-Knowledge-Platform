package com.jk.labs.vkp.company.dao.entity;

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

/** JPA entity for the {@code companies} table (h2 / postgres profiles). */
@Entity
@Table(name = "companies")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class CompEntity {

    @Id
    @Column(name = "company_id", length = 36, nullable = false, updatable = false)
    private String companyId;

    @Column(name = "name", length = 100, nullable = false)
    private String name;

    @Column(name = "description", length = 250)
    private String description;

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
