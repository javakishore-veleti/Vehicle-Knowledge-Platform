package com.jk.labs.vkp.datacollection.service.snapshot;

import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.Comparator;
import java.util.List;
import java.util.stream.Stream;

/**
 * Default backend: reads snapshots from the local filesystem (the same folder the crawl DAG writes when
 * its {@code storage_backend} is {@code local} — shared via a volume mount in compose / a RWX volume in k8s).
 */
@Component
@ConditionalOnProperty(name = "vkp.snapshot.backend", havingValue = "local", matchIfMissing = true)
@Slf4j
public class LocalSnapshotStore implements SnapshotStore {

    private final Path base;

    public LocalSnapshotStore(
            @Value("${vkp.snapshot.location:${datacollection.snapshot-dir:${user.home}/runtime_data/ai_projects/Vehicle-Knowledge-Platform/Crawling-Snapshot}}")
            String dir) {
        this.base = Path.of(dir).toAbsolutePath().normalize();
        log.info("Snapshot backend: local ({})", this.base);
    }

    @Override
    public List<String> listCompanies() {
        if (!Files.isDirectory(base)) {
            return List.of();
        }
        try (Stream<Path> s = Files.list(base)) {
            return s.filter(Files::isDirectory).map(p -> p.getFileName().toString()).sorted().toList();
        } catch (IOException e) {
            log.warn("listCompanies {}: {}", base, e.getMessage());
            return List.of();
        }
    }

    @Override
    public List<String> listFiles(String company, String subdir) {
        Path d = resolveKey((subdir == null || subdir.isBlank()) ? company : company + "/" + subdir);
        if (d == null || !Files.isDirectory(d)) {
            return List.of();
        }
        try (Stream<Path> s = Files.list(d)) {
            return s.filter(Files::isRegularFile).map(p -> p.getFileName().toString())
                    .sorted(Comparator.naturalOrder()).toList();
        } catch (IOException e) {
            return List.of();
        }
    }

    @Override
    public byte[] read(String relKey) {
        Path p = resolveKey(relKey);
        if (p == null || !Files.isRegularFile(p)) {
            return null;
        }
        try {
            return Files.readAllBytes(p);
        } catch (IOException e) {
            log.warn("read {}: {}", relKey, e.getMessage());
            return null;
        }
    }

    @Override
    public boolean exists(String relKey) {
        Path p = resolveKey(relKey);
        return p != null && Files.exists(p);
    }

    /** Resolve a relative key under the base, guarding against path traversal. */
    private Path resolveKey(String relKey) {
        if (relKey == null || relKey.isBlank() || relKey.contains("..")) {
            return null;
        }
        Path p = base.resolve(relKey).normalize();
        return p.startsWith(base) ? p : null;
    }
}
