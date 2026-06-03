package com.jk.labs.vkp.indexing.dao.entity;

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

/** Registry of indexing workflows (AIRFLOW DAGs or SPRING_AI executors). Can be 10k+. */
@Entity
@Table(name = "indexing_workflow")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class IndexingWorkflowEntity {

    @Id
    @Column(name = "wf_id", length = 36, nullable = false, updatable = false)
    private String wfId;

    @Column(name = "name", length = 150, nullable = false)
    private String name;

    /** AIRFLOW | SPRING_AI */
    @Column(name = "wf_type", length = 20, nullable = false)
    private String wfType;

    /** DAG id (AIRFLOW) or Spring-AI executor bean id (SPRING_AI). */
    @Column(name = "target_ref", length = 150)
    private String targetRef;

    @Column(name = "description", length = 500)
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
