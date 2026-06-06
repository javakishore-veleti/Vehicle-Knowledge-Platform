package com.jk.labs.vkp.vectorconfig.api.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** OpenAPI / Swagger UI metadata for the Vector Config Service. */
@Configuration
public class OpenApiConfig {
    @Bean
    public OpenAPI vectorConfigServiceOpenAPI() {
        return new OpenAPI().info(new Info()
                .title("VKP Vector Config Service API")
                .description("Admin-facing per-resource vector-store configuration (rule #3)")
                .version("0.1.0"));
    }
}
