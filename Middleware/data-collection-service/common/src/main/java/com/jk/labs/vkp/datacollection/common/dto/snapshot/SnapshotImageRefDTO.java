package com.jk.labs.vkp.datacollection.common.dto.snapshot;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class SnapshotImageRefDTO {

    private String imageId;
    private String src;
    private String file;
}
