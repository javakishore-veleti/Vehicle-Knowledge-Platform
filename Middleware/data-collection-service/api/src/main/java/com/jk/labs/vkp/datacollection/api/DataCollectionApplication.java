package com.jk.labs.vkp.datacollection.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

/**
 * Entry point for the VKP Data Collection Service. Discovers links only (via the
 * vkp_discover_resources DAG, triggered through airflow-adapter-service) and owns the
 * company_resource_graph.
 */
@SpringBootApplication(scanBasePackages = "com.jk.labs.vkp.datacollection")
@EntityScan(basePackages = "com.jk.labs.vkp.datacollection.dao.entity")
@EnableJpaRepositories(basePackages = "com.jk.labs.vkp.datacollection.dao.repository")
public class DataCollectionApplication {

    public static void main(String[] args) {
        SpringApplication.run(DataCollectionApplication.class, args);
    }
}
