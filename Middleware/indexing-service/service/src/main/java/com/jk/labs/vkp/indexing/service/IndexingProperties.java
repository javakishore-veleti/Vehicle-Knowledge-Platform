package com.jk.labs.vkp.indexing.service;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/** Indexing control-plane settings, bound from {@code indexing.*}. */
@Component
@ConfigurationProperties(prefix = "indexing")
@Getter
@Setter
public class IndexingProperties {

    /** Base URL of the Spring-AI executor (indexing-service-wfs-java). */
    private String wfsBaseUrl = "http://localhost:8087";

    /** Base URL the Airflow DAG (in the container) calls back to this control plane. */
    private String airflowCallbackBaseUrl = "http://host.docker.internal:8086";

    /** Base URL the DAG reads a company's snapshot pages from (data-collection-service). */
    private String dataCollectionBaseUrl = "http://host.docker.internal:8084";

    /** Default vector-store target type when not resolved from a credential. */
    private String defaultVectorStore = "pgvector";

    /** pgVector connection the DAG writes embeddings to (container-reachable host). */
    private String pgHost = "host.docker.internal";
    private int pgPort = 5432;
    private String pgDb = "vkp";
    private String pgUser = "vkp";
    private String pgPassword = "vkp";
}
