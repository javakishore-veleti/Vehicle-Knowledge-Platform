package com.jk.labs.vkp.datacollection.common.dto.snapshot;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.ArrayList;
import java.util.List;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ListPagesRespDTO {

    private String company;
    private List<SnapshotPageDTO> pages = new ArrayList<>();
    private int count;     // returned in this slice
    private int total;     // total pages in the snapshot (for the paginator)
    private int offset;
}
