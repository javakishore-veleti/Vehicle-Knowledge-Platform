package com.jk.labs.vkp.datacollection.service.snapshot;

import com.azure.identity.DefaultAzureCredentialBuilder;
import com.azure.storage.blob.BlobContainerClient;
import com.azure.storage.blob.BlobContainerClientBuilder;
import com.azure.storage.blob.models.BlobItem;
import com.azure.storage.blob.models.ListBlobsOptions;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.stereotype.Component;

import java.util.ArrayList;
import java.util.List;

/**
 * Azure Blob snapshot reader. Selected by {@code vkp.snapshot.backend=azure}; target via
 * {@code vkp.snapshot.location=my-container/prefix}. Auth via {@code AZURE_STORAGE_CONNECTION_STRING},
 * or {@code AZURE_STORAGE_ACCOUNT_URL} + DefaultAzureCredential (managed identity). Only compiled under
 * the {@code cloud-snapshot} Maven profile.
 */
@Component
@ConditionalOnProperty(name = "vkp.snapshot.backend", havingValue = "azure")
@Slf4j
public class AzureSnapshotStore implements SnapshotStore {

    private final String prefix;
    private final BlobContainerClient container;

    public AzureSnapshotStore(@Value("${vkp.snapshot.location:}") String location) {
        String[] cp = SnapshotLocations.containerPrefix(location);
        String containerName = cp[0];
        this.prefix = cp[1];
        String conn = System.getenv("AZURE_STORAGE_CONNECTION_STRING");
        if (conn != null && !conn.isBlank()) {
            this.container = new BlobContainerClientBuilder().connectionString(conn)
                    .containerName(containerName).buildClient();
        } else {
            String acct = System.getenv("AZURE_STORAGE_ACCOUNT_URL");
            if (acct == null || acct.isBlank()) {
                throw new IllegalStateException("Azure backend needs AZURE_STORAGE_CONNECTION_STRING "
                        + "or AZURE_STORAGE_ACCOUNT_URL.");
            }
            this.container = new BlobContainerClientBuilder().endpoint(acct)
                    .credential(new DefaultAzureCredentialBuilder().build())
                    .containerName(containerName).buildClient();
        }
        log.info("Snapshot backend: azure (container={}, prefix='{}')", containerName, prefix);
    }

    private String name(String rel) {
        return prefix + rel;
    }

    @Override
    public List<String> listCompanies() {
        List<String> out = new ArrayList<>();
        ListBlobsOptions opts = new ListBlobsOptions().setPrefix(prefix.isEmpty() ? null : prefix);
        for (BlobItem item : container.listBlobsByHierarchy("/", opts, null)) {
            if (Boolean.TRUE.equals(item.isPrefix())) {
                String n = item.getName().substring(prefix.length());
                if (n.endsWith("/")) {
                    n = n.substring(0, n.length() - 1);
                }
                if (!n.isBlank()) {
                    out.add(n);
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
        ListBlobsOptions opts = new ListBlobsOptions().setPrefix(p);
        for (BlobItem item : container.listBlobsByHierarchy("/", opts, null)) {
            if (!Boolean.TRUE.equals(item.isPrefix())) {
                String n = item.getName().substring(p.length());
                if (!n.isBlank() && n.indexOf('/') < 0) {
                    out.add(n);
                }
            }
        }
        out.sort(String::compareTo);
        return out;
    }

    @Override
    public byte[] read(String relKey) {
        var blob = container.getBlobClient(name(relKey));
        if (!blob.exists()) {
            return null;
        }
        return blob.downloadContent().toBytes();
    }

    @Override
    public boolean exists(String relKey) {
        return container.getBlobClient(name(relKey)).exists();
    }
}
