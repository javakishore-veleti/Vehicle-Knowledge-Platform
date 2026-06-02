package com.jk.labs.vkp.airflow.api.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** OpenAPI / Swagger UI metadata for the Airflow Adapter Service. */
@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI airflowAdapterOpenAPI() {
        return new OpenAPI().info(new Info()
                .title("VKP Airflow Adapter API")
                .description("Single gateway for triggering and monitoring Apache Airflow DAGs")
                .version("0.1.0"));
    }
}
