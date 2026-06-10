package com.jk.labs.vkp.datacollection.service;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.jk.labs.vkp.datacollection.common.dto.snapshot.ListPagesCtx;
import com.jk.labs.vkp.datacollection.common.dto.snapshot.ListPagesReqDTO;
import com.jk.labs.vkp.datacollection.common.dto.snapshot.ListPagesRespDTO;
import com.jk.labs.vkp.datacollection.common.dto.snapshot.ListSnapshotsCtx;
import com.jk.labs.vkp.datacollection.common.dto.snapshot.ListSnapshotsRespDTO;
import com.jk.labs.vkp.datacollection.common.dto.snapshot.SnapshotCompanyDTO;
import com.jk.labs.vkp.datacollection.common.dto.snapshot.SnapshotImageRefDTO;
import com.jk.labs.vkp.datacollection.common.dto.snapshot.SnapshotPageDTO;
import com.jk.labs.vkp.datacollection.common.error.ResourceNotFoundException;
import com.jk.labs.vkp.datacollection.service.snapshot.SnapshotStore;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.util.ArrayList;
import java.util.List;

/**
 * Reads crawl snapshots through a {@link SnapshotStore} (local FS, S3, Azure Blob, or GCS — selected by
 * {@code vkp.snapshot.backend}), so the Browser works regardless of where the crawl DAG wrote the bytes.
 * Pagination is seek-by-file: each crawl-NNNNN.json holds exactly {@code PAGE_SIZE} elements, so a page
 * request reads only the file(s) covering [offset, offset+limit) — never the whole snapshot.
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class SnapshotService {

    private static final int PAGE_SIZE = 250;       // must match the crawl DAG's BATCH
    private static final int TEXT_PREVIEW = 2000;
    private static final int MAX_LIMIT = 200;

    private final ObjectMapper mapper;
    private final SnapshotStore store;

    /** Raw image bytes + content type for serving. */
    public record ImageData(byte[] data, String contentType) {
    }

    /** Lightweight page reference (no text/images) for registering pages as graph rows. */
    public record PageRef(String url, String title, int depth) {
    }

    /** Read every page's url/title/depth across all crawl files (used by graph registration). */
    public List<PageRef> collectPageRefs(String company) {
        validateCompany(company);
        List<PageRef> out = new ArrayList<>();
        for (String key : crawlFiles(company)) {
            JsonNode arr = readJson(key);
            if (arr == null || !arr.isArray()) {
                continue;
            }
            for (JsonNode el : arr) {
                String url = el.path("url").asText(null);
                if (url == null || url.isBlank()) {
                    continue;
                }
                out.add(new PageRef(url, el.path("title").asText(null), el.path("depth").asInt(0)));
            }
        }
        return out;
    }

    public void listCompanies(ListSnapshotsCtx ctx) {
        List<SnapshotCompanyDTO> out = new ArrayList<>();
        for (String company : store.listCompanies()) {
            out.add(readCompany(company));
        }
        ctx.setRespDTO(new ListSnapshotsRespDTO(out, out.size()));
    }

    public void listPages(ListPagesCtx ctx) {
        ListPagesReqDTO req = ctx.getReqDTO();
        validateCompany(req.getCompany());
        int offset = Math.max(0, req.getOffset());
        int limit = req.getLimit() > 0 ? Math.min(req.getLimit(), MAX_LIMIT) : 50;

        List<String> files = crawlFiles(req.getCompany());
        int total = totalPages(files);

        List<SnapshotPageDTO> pages = new ArrayList<>();
        int startIdx = offset / PAGE_SIZE;
        int within = offset % PAGE_SIZE;
        for (int fi = startIdx; fi < files.size() && pages.size() < limit; fi++) {
            JsonNode arr = readJson(files.get(fi));
            if (arr == null || !arr.isArray()) {
                continue;
            }
            int start = (fi == startIdx) ? within : 0;
            for (int i = start; i < arr.size() && pages.size() < limit; i++) {
                pages.add(toPage(arr.get(i), req.isFull()));
            }
        }
        ctx.setRespDTO(new ListPagesRespDTO(req.getCompany(), pages, pages.size(), total, offset));
    }

    public ImageData readImage(String company, String imageId) {
        validateCompany(company);
        if (imageId == null || !imageId.matches("[a-fA-F0-9]{8,64}")) {
            throw new ResourceNotFoundException("Invalid image id");
        }
        String file = store.listFiles(company, "images").stream()
                .filter(n -> n.startsWith(imageId + "."))
                .findFirst()
                .orElseThrow(() -> new ResourceNotFoundException("Image not found: " + imageId));
        byte[] data = store.read(company + "/images/" + file);
        if (data == null) {
            throw new ResourceNotFoundException("Image not readable: " + imageId);
        }
        String ct = contentType(file);
        if ("application/octet-stream".equals(ct)) {
            String sniffed = sniff(data);
            if (sniffed != null) {
                ct = sniffed;
            }
        }
        return new ImageData(data, ct);
    }

    // ------------------------------------------------------------------
    private SnapshotCompanyDTO readCompany(String company) {
        boolean completed = store.exists(company + "/__COMPLETED__/manifest.json");
        List<String> files = crawlFiles(company);
        int pages = totalPages(files);
        int images = store.listFiles(company, "images").size();
        String completedAt = null;
        if (completed) {
            JsonNode m = readJson(company + "/__COMPLETED__/manifest.json");
            if (m != null) {
                completedAt = m.path("completed_at").asText(null);
            }
        }
        return SnapshotCompanyDTO.builder()
                .company(company).completed(completed)
                .pages(pages).files(files.size()).images(images).completedAt(completedAt)
                .build();
    }

    /** Relative keys of the company's crawl-*.json files, sorted (the store already sorts leaf names). */
    private List<String> crawlFiles(String company) {
        List<String> out = new ArrayList<>();
        for (String name : store.listFiles(company, "")) {
            if (name.startsWith("crawl-") && name.endsWith(".json")) {
                out.add(company + "/" + name);
            }
        }
        return out;
    }

    /** total = (numFiles-1)*PAGE_SIZE + size(last file); reads only the last file. */
    private int totalPages(List<String> files) {
        if (files.isEmpty()) {
            return 0;
        }
        JsonNode last = readJson(files.get(files.size() - 1));
        int lastCount = (last != null && last.isArray()) ? last.size() : 0;
        return (files.size() - 1) * PAGE_SIZE + lastCount;
    }

    private SnapshotPageDTO toPage(JsonNode el, boolean full) {
        String text = el.path("text").asText("");
        List<SnapshotImageRefDTO> images = new ArrayList<>();
        JsonNode imgs = el.path("images");
        if (imgs.isArray()) {
            imgs.forEach(im -> images.add(SnapshotImageRefDTO.builder()
                    .imageId(im.path("image_id").asText(null))
                    .src(im.path("src").asText(null))
                    .file(im.path("file").asText(null))
                    .build()));
        }
        String outText = (full || text.length() <= TEXT_PREVIEW) ? text : text.substring(0, TEXT_PREVIEW);
        return SnapshotPageDTO.builder()
                .url(el.path("url").asText(null))
                .depth(el.path("depth").asInt(0))
                .title(el.path("title").asText(null))
                .text(outText)
                .textLength(text.length())
                .images(images)
                .linksCount(el.path("links_count").asInt(0))
                .fetchedAt(el.path("fetched_at").asText(null))
                .build();
    }

    private void validateCompany(String company) {
        if (company == null || company.isBlank() || company.contains("/") || company.contains("..")) {
            throw new ResourceNotFoundException("Invalid company");
        }
    }

    private JsonNode readJson(String relKey) {
        byte[] data = store.read(relKey);
        if (data == null) {
            return null;
        }
        try {
            return mapper.readTree(data);
        } catch (IOException e) {
            log.warn("Failed to parse {}: {}", relKey, e.getMessage());
            return null;
        }
    }

    /** Sniff image type from magic bytes (for files saved with an unknown extension). */
    private static String sniff(byte[] d) {
        if (d.length >= 3 && (d[0] & 0xFF) == 0xFF && (d[1] & 0xFF) == 0xD8 && (d[2] & 0xFF) == 0xFF) {
            return "image/jpeg";
        }
        if (d.length >= 4 && (d[0] & 0xFF) == 0x89 && d[1] == 'P' && d[2] == 'N' && d[3] == 'G') {
            return "image/png";
        }
        if (d.length >= 3 && d[0] == 'G' && d[1] == 'I' && d[2] == 'F') {
            return "image/gif";
        }
        if (d.length >= 12 && d[0] == 'R' && d[1] == 'I' && d[2] == 'F' && d[3] == 'F'
                && d[8] == 'W' && d[9] == 'E' && d[10] == 'B' && d[11] == 'P') {
            return "image/webp";
        }
        if (d.length >= 2 && d[0] == 'B' && d[1] == 'M') {
            return "image/bmp";
        }
        String head = new String(d, 0, Math.min(d.length, 64)).trim().toLowerCase();
        if (head.startsWith("<svg") || head.startsWith("<?xml")) {
            return "image/svg+xml";
        }
        return null;
    }

    private static String contentType(String filename) {
        String f = filename.toLowerCase();
        if (f.endsWith(".png")) return "image/png";
        if (f.endsWith(".jpg") || f.endsWith(".jpeg")) return "image/jpeg";
        if (f.endsWith(".gif")) return "image/gif";
        if (f.endsWith(".webp")) return "image/webp";
        if (f.endsWith(".svg")) return "image/svg+xml";
        if (f.endsWith(".avif")) return "image/avif";
        if (f.endsWith(".bmp")) return "image/bmp";
        return "application/octet-stream";
    }
}
