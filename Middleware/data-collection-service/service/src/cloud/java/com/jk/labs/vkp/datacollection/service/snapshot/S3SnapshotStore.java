package com.jk.labs.vkp.datacollection.service.snapshot;

import jakarta.annotation.PreDestroy;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;
import software.amazon.awssdk.services.s3.S3Client;
import software.amazon.awssdk.services.s3.model.CommonPrefix;
import software.amazon.awssdk.services.s3.model.GetObjectRequest;
import software.amazon.awssdk.services.s3.model.HeadObjectRequest;
import software.amazon.awssdk.services.s3.model.ListObjectsV2Request;
import software.amazon.awssdk.services.s3.model.ListObjectsV2Response;
import software.amazon.awssdk.services.s3.model.NoSuchKeyException;
import software.amazon.awssdk.services.s3.model.S3Object;

import java.util.ArrayList;
import java.util.List;

/**
 * AWS S3 snapshot reader. Selected by {@code vkp.snapshot.backend=s3}; target via
 * {@code vkp.snapshot.location=s3://my-bucket/prefix}. Credentials/region resolve through the standard
 * AWS chain (IAM role / AWS_* env / profile; region via AWS_REGION). Only compiled under the
 * {@code cloud-snapshot} Maven profile.
 */
@Component
@ConditionalOnProperty(name = "vkp.snapshot.backend", havingValue = "s3")
@Slf4j
public class S3SnapshotStore implements SnapshotStore {

    private final String bucket;
    private final String prefix;
    private final S3Client s3;

    public S3SnapshotStore(@Value("${vkp.snapshot.location:}") String location) {
        String[] bp = SnapshotLocations.bucketPrefix(location, "s3");
        this.bucket = bp[0];
        this.prefix = bp[1];
        this.s3 = S3Client.create();
        log.info("Snapshot backend: s3 (bucket={}, prefix='{}')", bucket, prefix);
    }

    private String key(String rel) {
        return prefix + rel;
    }

    @Override
    public List<String> listCompanies() {
        List<String> out = new ArrayList<>();
        String token = null;
        do {
            ListObjectsV2Response r = s3.listObjectsV2(ListObjectsV2Request.builder()
                    .bucket(bucket).prefix(prefix).delimiter("/").continuationToken(token).build());
            for (CommonPrefix cp : r.commonPrefixes()) {
                String name = cp.prefix().substring(prefix.length());
                if (name.endsWith("/")) {
                    name = name.substring(0, name.length() - 1);
                }
                if (!name.isBlank()) {
                    out.add(name);
                }
            }
            token = Boolean.TRUE.equals(r.isTruncated()) ? r.nextContinuationToken() : null;
        } while (token != null);
        out.sort(String::compareTo);
        return out;
    }

    @Override
    public List<String> listFiles(String company, String subdir) {
        String p = key(company + "/" + (subdir == null || subdir.isBlank() ? "" : subdir + "/"));
        List<String> out = new ArrayList<>();
        String token = null;
        do {
            ListObjectsV2Response r = s3.listObjectsV2(ListObjectsV2Request.builder()
                    .bucket(bucket).prefix(p).delimiter("/").continuationToken(token).build());
            for (S3Object o : r.contents()) {
                String name = o.key().substring(p.length());
                if (!name.isBlank() && name.indexOf('/') < 0) {
                    out.add(name);
                }
            }
            token = Boolean.TRUE.equals(r.isTruncated()) ? r.nextContinuationToken() : null;
        } while (token != null);
        out.sort(String::compareTo);
        return out;
    }

    @Override
    public byte[] read(String relKey) {
        try {
            return s3.getObjectAsBytes(GetObjectRequest.builder().bucket(bucket).key(key(relKey)).build())
                    .asByteArray();
        } catch (NoSuchKeyException e) {
            return null;
        }
    }

    @Override
    public boolean exists(String relKey) {
        try {
            s3.headObject(HeadObjectRequest.builder().bucket(bucket).key(key(relKey)).build());
            return true;
        } catch (NoSuchKeyException e) {
            return false;
        }
    }

    @PreDestroy
    public void close() {
        s3.close();
    }
}
