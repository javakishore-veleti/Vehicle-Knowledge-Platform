package com.jk.labs.vkp.datacollection.api.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** OpenAPI / Swagger UI metadata for the Data Collection Service. */
@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI dataCollectionOpenAPI() {
        return new OpenAPI().info(new Info()
                .title("VKP Data Collection Service API")
                .description("Trigger link discovery (via Airflow) and read the company resource graph")
                .version("0.1.0"));
    }
}
