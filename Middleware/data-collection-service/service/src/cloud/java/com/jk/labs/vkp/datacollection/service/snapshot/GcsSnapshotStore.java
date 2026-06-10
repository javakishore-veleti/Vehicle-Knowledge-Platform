package com.jk.labs.vkp.datacollection.service.snapshot;

import com.google.cloud.storage.Blob;
import com.google.cloud.storage.BlobId;
import com.google.cloud.storage.Storage;
import com.google.cloud.storage.StorageOptions;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

/**
 * Google Cloud Storage snapshot reader. Selected by {@code vkp.snapshot.backend=gcs}; target via
 * {@code vkp.snapshot.location=gs://my-bucket/prefix}. Auth via {@code GOOGLE_APPLICATION_CREDENTIALS}
 * (service-account JSON) or Application Default Credentials. Only compiled under the
 * {@code cloud-snapshot} Maven profile.
 */
@Component
@ConditionalOnProperty(name = "vkp.snapshot.backend", havingValue = "gcs")
@Slf4j
public class GcsSnapshotStore implements SnapshotStore {

    private final String bucket;
    private final String prefix;
    private final Storage storage;

    public GcsSnapshotStore(@Value("${vkp.snapshot.location:}") String location) {
        String[] bp = SnapshotLocations.bucketPrefix(location, "gs");
        this.bucket = bp[0];
        this.prefix = bp[1];
        this.storage = StorageOptions.getDefaultInstance().getService();
        log.info("Snapshot backend: gcs (bucket={}, prefix='{}')", bucket, prefix);
    }

    private String name(String rel) {
        return prefix + rel;
    }

    @Override
    public List<String> listCompanies() {
        List<String> out = new ArrayList<>();
        for (Blob b : storage.list(bucket, Storage.BlobListOption.prefix(prefix),
                Storage.BlobListOption.currentDirectory()).iterateAll()) {
            String n = b.getName();
            if (n.endsWith("/")) {                       // a "directory" = a company folder
                String name = n.substring(prefix.length(), n.length() - 1);
                if (!name.isBlank() && name.indexOf('/') < 0) {
                    out.add(name);
                }
            }
        }
        out.sort(String::compareTo);
        return out;
    }

    @Override
    public List<String> listFiles(String company, String subdir) {
        String p = name(company + "/" + (subdir == null || subdir.isBlank() ? "" : subdir + "/"));
        List<String> out = new ArrayList<>();
        for (Blob b : storage.list(bucket, Storage.BlobListOption.prefix(p),
                Storage.BlobListOption.currentDirectory()).iterateAll()) {
            String n = b.getName();
            if (!n.endsWith("/")) {                       // a file, not a sub-directory
                String leaf = n.substring(p.length());
                if (!leaf.isBlank() && leaf.indexOf('/') < 0) {
                    out.add(leaf);
                }
            }
        }
        out.sort(String::compareTo);
        return out;
    }

    @Override
    public byte[] read(String relKey) {
        Blob b = storage.get(BlobId.of(bucket, name(relKey)));
        return (b == null || !b.exists()) ? null : b.getContent();
    }

    @Override
    public boolean exists(String relKey) {
        Blob b = storage.get(BlobId.of(bucket, name(relKey)));
        return b != null && b.exists();
    }
}
