package com.jk.labs.vkp.user.service;

import lombok.Getter;
import lombok.Setter;
import org.springframework.boot.context.properties.ConfigurationProperties;
import org.springframework.stereotype.Component;

/** JWT signing configuration, bound from {@code jwt.*} in application config. */
@Component
@ConfigurationProperties(prefix = "jwt")
@Getter
@Setter
public class JwtProperties {

    /** HMAC signing secret. Must be >= 32 bytes for HS256. Override per environment. */
    private String secret = "change-me-dev-secret-please-override-in-prod-0123456789";

    /** Token lifetime in minutes. */
    private long expirationMinutes = 60;
}
