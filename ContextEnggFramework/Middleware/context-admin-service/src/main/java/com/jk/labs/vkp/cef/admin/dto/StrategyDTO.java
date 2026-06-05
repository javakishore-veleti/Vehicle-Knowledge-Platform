package com.jk.labs.vkp.cef.admin.dto;

import jakarta.validation.constraints.NotBlank;
import lombok.Data;

@Data
public class StrategyDTO {
    private String id;
    @NotBlank
    private String name;
    private String description;
    private boolean selectionEnabled = true;
    private boolean compressionEnabled = true;
    private boolean orderingEnabled = true;
    private boolean isolationEnabled = false;
    private boolean formatEnabled = true;
    private int charBudget = 6000;
    private String status = "ACTIVE";
}
