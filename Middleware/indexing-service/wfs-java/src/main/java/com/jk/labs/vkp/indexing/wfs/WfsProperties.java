package com.jk.labs.vkp.indexing.wfs;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/** Executor settings, bound from {@code wfs.*}. */
@Component
@ConfigurationProperties(prefix = "wfs")
@Getter
@Setter
public class WfsProperties {

    /** Base URL of the indexing control plane (for status callbacks). */
    private String controlBaseUrl = "http://localhost:8086";

    /** data-collection-service base URL (snapshot pages + resource graph source). */
    private String dataCollectionBaseUrl = "http://localhost:8084";

    /** Chunking defaults (overridden per-run by the index formula's params). */
    private int chunkSize = 512;
    private int chunkOverlap = 64;
    private int dim = 384;
}
