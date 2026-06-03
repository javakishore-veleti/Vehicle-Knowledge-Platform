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
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Stream;

/**
 * Reads crawl snapshots from the local filesystem (the same folder the crawl DAG writes,
 * which this host-run service can read directly). Pagination is seek-by-file: each
 * crawl-NNNNN.json holds exactly {@code PAGE_SIZE} elements, so a page request reads only
 * the file(s) covering [offset, offset+limit) — never the whole snapshot.
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class SnapshotService {

    private static final int PAGE_SIZE = 250;       // must match the crawl DAG's BATCH
    private static final int TEXT_PREVIEW = 2000;
    private static final int MAX_LIMIT = 200;

    private final ObjectMapper mapper;

    @Value("${datacollection.snapshot-dir:${user.home}/runtime_data/ai_projects/Vehicle-Knowledge-Platform/Crawling-Snapshot}")
    private String snapshotDir;

    /** Raw image bytes + content type for serving. */
    public record ImageData(byte[] data, String contentType) {
    }

    /** Lightweight page reference (no text/images) for registering pages as graph rows. */
    public record PageRef(String url, String title, int depth) {
    }

    /** Read every page's url/title/depth across all crawl files (used by graph registration). */
    public List<PageRef> collectPageRefs(String company) {
        Path dir = resolveCompanyDir(company);
        List<PageRef> out = new ArrayList<>();
        for (Path f : crawlFiles(dir)) {
            JsonNode arr = readJson(f);
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
        Path base = Path.of(snapshotDir);
        List<SnapshotCompanyDTO> out = new ArrayList<>();
        if (Files.isDirectory(base)) {
            try (Stream<Path> dirs = Files.list(base)) {
                dirs.filter(Files::isDirectory).sorted().forEach(d -> out.add(readCompany(d)));
            } catch (IOException e) {
                log.warn("Failed to list snapshot dir {}: {}", base, e.getMessage());
            }
        }
        ctx.setRespDTO(new ListSnapshotsRespDTO(out, out.size()));
    }

    public void listPages(ListPagesCtx ctx) {
        ListPagesReqDTO req = ctx.getReqDTO();
        Path dir = resolveCompanyDir(req.getCompany());
        int offset = Math.max(0, req.getOffset());
        int limit = req.getLimit() > 0 ? Math.min(req.getLimit(), MAX_LIMIT) : 50;

        List<Path> files = crawlFiles(dir);
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
        if (imageId == null || !imageId.matches("[a-fA-F0-9]{8,64}")) {
            throw new ResourceNotFoundException("Invalid image id");
        }
        Path imagesDir = resolveCompanyDir(company).resolve("images");
        if (!Files.isDirectory(imagesDir)) {
            throw new ResourceNotFoundException("No images for company");
        }
        try (Stream<Path> s = Files.list(imagesDir)) {
            Path file = s.filter(p -> p.getFileName().toString().startsWith(imageId + ".")).findFirst()
                    .orElseThrow(() -> new ResourceNotFoundException("Image not found: " + imageId));
            byte[] data = Files.readAllBytes(file);
            String ct = contentType(file.getFileName().toString());
            if ("application/octet-stream".equals(ct)) {
                String sniffed = sniff(data);
                if (sniffed != null) {
                    ct = sniffed;
                }
            }
            return new ImageData(data, ct);
        } catch (IOException e) {
            throw new ResourceNotFoundException("Image not readable: " + imageId);
        }
    }

    // ------------------------------------------------------------------
    private SnapshotCompanyDTO readCompany(Path dir) {
        String name = dir.getFileName().toString();
        Path manifest = dir.resolve("__COMPLETED__").resolve("manifest.json");
        boolean completed = Files.exists(manifest);
        List<Path> files = crawlFiles(dir);
        int pages = totalPages(files);
        int images = countDir(dir.resolve("images"));
        String completedAt = null;
        if (completed) {
            JsonNode m = readJson(manifest);
            if (m != null) {
                completedAt = m.path("completed_at").asText(null);
            }
        }
        return SnapshotCompanyDTO.builder()
                .company(name).completed(completed)
                .pages(pages).files(files.size()).images(images).completedAt(completedAt)
                .build();
    }

    private List<Path> crawlFiles(Path dir) {
        if (!Files.isDirectory(dir)) {
            return List.of();
        }
        try (Stream<Path> s = Files.list(dir)) {
            return s.filter(p -> {
                String n = p.getFileName().toString();
                return n.startsWith("crawl-") && n.endsWith(".json");
            }).sorted(Comparator.comparing(p -> p.getFileName().toString())).toList();
        } catch (IOException e) {
            return List.of();
        }
    }

    /** total = (numFiles-1)*PAGE_SIZE + size(last file); reads only the last file. */
    private int totalPages(List<Path> files) {
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

    private Path resolveCompanyDir(String company) {
        if (company == null || company.isBlank() || company.contains("/") || company.contains("..")) {
            throw new ResourceNotFoundException("Invalid company");
        }
        Path base = Path.of(snapshotDir).toAbsolutePath().normalize();
        Path dir = base.resolve(company).normalize();
        if (!dir.startsWith(base) || !Files.isDirectory(dir)) {
            throw new ResourceNotFoundException("Snapshot not found: " + company);
        }
        return dir;
    }

    private JsonNode readJson(Path file) {
        try {
            return mapper.readTree(file.toFile());
        } catch (IOException e) {
            log.warn("Failed to read {}: {}", file, e.getMessage());
            return null;
        }
    }

    private int countDir(Path dir) {
        if (!Files.isDirectory(dir)) {
            return 0;
        }
        try (Stream<Path> s = Files.list(dir)) {
            return (int) s.filter(Files::isRegularFile).count();
        } catch (IOException e) {
            return 0;
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
