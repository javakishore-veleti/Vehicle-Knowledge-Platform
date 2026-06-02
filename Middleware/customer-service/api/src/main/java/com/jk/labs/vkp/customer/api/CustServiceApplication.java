package com.jk.labs.vkp.customer.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

/**
 * Entry point for the VKP Customer Management Service (Admin).
 *
 * Component scan, entity scan, and repository scan are widened to the service root
 * package because beans live across sibling Maven modules (api / service / dao).
 */
@SpringBootApplication(scanBasePackages = "com.jk.labs.vkp.customer")
@EntityScan(basePackages = "com.jk.labs.vkp.customer.dao.entity")
@EnableJpaRepositories(basePackages = "com.jk.labs.vkp.customer.dao.repository")
public class CustServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(CustServiceApplication.class, args);
    }
}
