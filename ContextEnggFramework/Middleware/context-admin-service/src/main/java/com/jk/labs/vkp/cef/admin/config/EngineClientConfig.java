package com.jk.labs.vkp.cef.admin.config;

import io.swagger.v3.oas.models.OpenAPI;
import io.swagger.v3.oas.models.info.Info;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class EngineClientConfig {

    @Bean
    public OpenAPI cefOpenApi() {
        return new OpenAPI().info(new Info().title("CEF Context Admin Service").version("0.1.0"));
    }
}
