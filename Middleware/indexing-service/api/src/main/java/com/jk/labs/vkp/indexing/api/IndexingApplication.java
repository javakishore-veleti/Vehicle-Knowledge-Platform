package com.jk.labs.vkp.indexing.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

/**
 * Entry point for the VKP Indexing Service control plane (port 8086). Owns the indexing
 * registry/metadata (index_formula, provider_credentials, indexing_workflow,
 * resource_graph_index_log), dedups, and routes runs to AIRFLOW DAGs or the SPRING_AI
 * executor (indexing-service-wfs-java). It never embeds — it orchestrates.
 */
@SpringBootApplication(scanBasePackages = "com.jk.labs.vkp.indexing")
@EntityScan(basePackages = "com.jk.labs.vkp.indexing.dao.entity")
@EnableJpaRepositories(basePackages = "com.jk.labs.vkp.indexing.dao.repository")
public class IndexingApplication {

    public static void main(String[] args) {
        SpringApplication.run(IndexingApplication.class, args);
    }
}
