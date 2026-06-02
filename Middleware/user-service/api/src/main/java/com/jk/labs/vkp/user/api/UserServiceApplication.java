package com.jk.labs.vkp.user.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.boot.autoconfigure.domain.EntityScan;
import org.springframework.data.jpa.repository.config.EnableJpaRepositories;

/**
 * Entry point for the VKP User Service (customer-facing: signup, signin, password reset, profile).
 *
 * Scans are widened to the service root package because beans live across sibling
 * Maven modules (api / service / dao).
 */
@SpringBootApplication(scanBasePackages = "com.jk.labs.vkp.user")
@EntityScan(basePackages = "com.jk.labs.vkp.user.dao.entity")
@EnableJpaRepositories(basePackages = "com.jk.labs.vkp.user.dao.repository")
public class UserServiceApplication {

    public static void main(String[] args) {
        SpringApplication.run(UserServiceApplication.class, args);
    }
}
