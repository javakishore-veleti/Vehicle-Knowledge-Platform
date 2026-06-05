package com.jk.labs.vkp.cef.admin.entity;

import jakarta.persistence.Column;
import jakarta.persistence.Entity;
import jakarta.persistence.Id;
import jakarta.persistence.Table;
import lombok.Getter;
import lombok.Setter;

import java.time.Instant;

/** A named Context-Engineering strategy config: which of the 5 strategies are on + the context budget. */
@Entity
@Table(name = "cef_strategy")
@Getter
@Setter
public class CefStrategyEntity {
    @Id
    @Column(length = 36)
    private String id;
    @Column(nullable = false, length = 150)
    private String name;
    @Column(length = 500)
    private String description;
    private boolean selectionEnabled = true;
    private boolean compressionEnabled = true;
    private boolean orderingEnabled = true;
    private boolean isolationEnabled = false;
    private boolean formatEnabled = true;
    private int charBudget = 6000;
    @Column(length = 15)
    private String status = "ACTIVE";
    private Instant createdDt;
    private Instant updatedDt;
}
