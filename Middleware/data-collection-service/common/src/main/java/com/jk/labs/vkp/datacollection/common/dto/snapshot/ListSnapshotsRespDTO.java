package com.jk.labs.vkp.datacollection.common.dto.snapshot;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ListSnapshotsRespDTO {

    private List<SnapshotCompanyDTO> companies = new ArrayList<>();
    private int count;
}
