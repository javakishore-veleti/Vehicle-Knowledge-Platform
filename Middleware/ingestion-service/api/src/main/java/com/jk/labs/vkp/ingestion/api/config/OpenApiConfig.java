package com.jk.labs.vkp.ingestion.api.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** OpenAPI / Swagger UI metadata for the Ingestion Service. */
@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI ingestionOpenAPI() {
        return new OpenAPI().info(new Info()
                .title("VKP Ingestion Service API")
                .description("Trigger content ingestion (crawl + extract via Airflow) and read extracted content")
                .version("0.1.0"));
    }
}
