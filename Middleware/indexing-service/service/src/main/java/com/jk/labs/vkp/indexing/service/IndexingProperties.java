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

    /** Default vector-store target type when not resolved from a credential. */
    private String defaultVectorStore = "pgvector";
}
