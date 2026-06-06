package com.jk.labs.vkp.vectorconfig.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

/**
 * Entry point for the VKP Vector Config Service (Admin).
 *
 * Scans are widened to the service root package because beans live across sibling Maven
 * modules (api / service / dao).
 */
@SpringBootApplication(scanBasePackages = "com.jk.labs.vkp.vectorconfig")
@EntityScan(basePackages = "com.jk.labs.vkp.vectorconfig.dao.entity")
@EnableJpaRepositories(basePackages = "com.jk.labs.vkp.vectorconfig.dao.repository")
public class VecCfgServiceApplication {
    public static void main(String[] args) {
        SpringApplication.run(VecCfgServiceApplication.class, args);
    }
}
