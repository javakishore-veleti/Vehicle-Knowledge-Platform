package com.jk.labs.vkp.customer.api.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** OpenAPI / Swagger UI metadata for the Customer Service. */
@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI customerServiceOpenAPI() {
        return new OpenAPI().info(new Info()
                .title("VKP Customer Service API")
                .description("Admin-facing Customer and Customer Resource CRUD")
                .version("0.1.0"));
    }
}
