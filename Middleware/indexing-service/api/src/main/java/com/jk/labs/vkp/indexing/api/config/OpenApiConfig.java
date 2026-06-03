package com.jk.labs.vkp.indexing.api.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** OpenAPI / Swagger UI metadata for the Indexing Service. */
@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI indexingOpenAPI() {
        return new OpenAPI().info(new Info()
                .title("VKP Indexing Service API")
                .description("Indexing control plane: registry, formulas, credentials, trigger, logs")
                .version("0.1.0"));
    }
}
