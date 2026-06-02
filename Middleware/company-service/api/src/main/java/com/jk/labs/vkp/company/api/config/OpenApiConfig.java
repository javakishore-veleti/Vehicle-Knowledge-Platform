package com.jk.labs.vkp.company.api.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** OpenAPI / Swagger UI metadata for the Company Service. */
@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI companyServiceOpenAPI() {
        return new OpenAPI().info(new Info()
                .title("VKP Company Service API")
                .description("Admin-facing Company and Company Resource CRUD")
                .version("0.1.0"));
    }
}
