package com.jk.labs.vkp.company.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

/**
 * Entry point for the VKP Company Management Service (Admin).
 *
 * Component scan, entity scan, and repository scan are widened to the service root
 * package because beans live across sibling Maven modules (api / service / dao).
 */
@SpringBootApplication(scanBasePackages = "com.jk.labs.vkp.company")
@EntityScan(basePackages = "com.jk.labs.vkp.company.dao.entity")
@EnableJpaRepositories(basePackages = "com.jk.labs.vkp.company.dao.repository")
public class CompServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(CompServiceApplication.class, args);
    }
}
