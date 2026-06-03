package com.jk.labs.vkp.datacollection.api.controller;

import com.jk.labs.vkp.datacollection.common.api.ApiRoutes;
import com.jk.labs.vkp.datacollection.common.dto.snapshot.ListPagesCtx;
import com.jk.labs.vkp.datacollection.common.dto.snapshot.ListPagesReqDTO;
import com.jk.labs.vkp.datacollection.common.dto.snapshot.ListPagesRespDTO;
import com.jk.labs.vkp.datacollection.common.dto.snapshot.ListSnapshotsCtx;
import com.jk.labs.vkp.datacollection.common.dto.snapshot.ListSnapshotsReqDTO;
import com.jk.labs.vkp.datacollection.common.dto.snapshot.ListSnapshotsRespDTO;
import com.jk.labs.vkp.datacollection.service.SnapshotService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.CacheControl;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestParam;
import org.springframework.web.bind.annotation.RestController;

import java.util.concurrent.TimeUnit;

/** Read-only browser over the crawl filesystem snapshots (server-side paginated). */
@RestController
@RequiredArgsConstructor
public class SnapshotController {

    private final SnapshotService snapshotService;

    @GetMapping(ApiRoutes.SNAPSHOTS)
    public ListSnapshotsRespDTO snapshots() {
        ListSnapshotsCtx ctx = new ListSnapshotsCtx();
        ctx.setReqDTO(new ListSnapshotsReqDTO());
        snapshotService.listCompanies(ctx);
        return ctx.getRespDTO();
    }

    @GetMapping(ApiRoutes.SNAPSHOT_PAGES)
    public ListPagesRespDTO pages(@PathVariable String company,
                                  @RequestParam(defaultValue = "0") int offset,
                                  @RequestParam(defaultValue = "50") int limit) {
        ListPagesCtx ctx = new ListPagesCtx();
        ctx.setReqDTO(new ListPagesReqDTO(company, offset, limit));
        snapshotService.listPages(ctx);
        return ctx.getRespDTO();
    }

    @GetMapping(ApiRoutes.SNAPSHOT_IMAGE)
    public ResponseEntity<byte[]> image(@PathVariable String company, @PathVariable String imageId) {
        SnapshotService.ImageData img = snapshotService.readImage(company, imageId);
        return ResponseEntity.ok()
                .contentType(MediaType.parseMediaType(img.contentType()))
                .cacheControl(CacheControl.maxAge(1, TimeUnit.HOURS))
                .body(img.data());
    }
}
