package com.jk.labs.vkp.datacollection.service.snapshot;

import java.util.List;

/**
 * Backend-agnostic read access to crawl snapshots. The crawl DAG writes snapshots to one of several
 * storage backends (local filesystem, AWS S3, Azure Blob, Google Cloud Storage) selected by its
 * {@code storage_backend} toggle; the Snapshot Browser reads them back through this interface so the
 * same browse/paginate logic works regardless of where the bytes live.
 *
 * <p>Relative keys are POSIX-style {@code "<company>/<...>"} paths (e.g. {@code "Toyota/crawl-00001.json"},
 * {@code "Toyota/images/<uuid>.png"}, {@code "Toyota/__COMPLETED__/manifest.json"}); each implementation
 * maps them onto its medium (a path under a base dir, or an object key under a bucket/container prefix).
 */
public interface SnapshotStore {

    /** Company names directly under the snapshot root (the top-level "folders"). */
    List<String> listCompanies();

    /** Leaf file names directly under {@code "<company>/<subdir>"} (subdir "" = the company root). */
    List<String> listFiles(String company, String subdir);

    /** Bytes for a relative key {@code "<company>/<...>"}, or {@code null} if it does not exist. */
    byte[] read(String relKey);

    /** Whether a relative key exists. */
    boolean exists(String relKey);
}
