package com.jk.labs.vkp.user.api.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

/** OpenAPI / Swagger UI metadata for the User Service. */
@Configuration
public class OpenApiConfig {

    @Bean
    public OpenAPI userServiceOpenAPI() {
        return new OpenAPI().info(new Info()
                .title("VKP User Service API")
                .description("Customer-facing user signup, signin, password reset, and profile")
                .version("0.1.0"));
    }
}
