package com.jk.labs.vkp.security;

import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.core.Ordered;

/**
 * Auto-registers the {@link SessionCryptoService} + {@link SessionCryptoFilter}. A microservice just
 * adds the {@code vkp-session-security} dependency and (optionally) sets {@code vkp.session.*}.
 */
@AutoConfiguration
@EnableConfigurationProperties(SessionSecurityProperties.class)
@ConditionalOnProperty(prefix = "vkp.session", name = "enabled", matchIfMissing = true)
public class SessionSecurityAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public SessionCryptoService sessionCryptoService(SessionSecurityProperties props) {
        return new SessionCryptoService(props.getSecret());
    }

    @Bean
    public FilterRegistrationBean<SessionCryptoFilter> vkpSessionCryptoFilter(
            SessionCryptoService crypto, SessionSecurityProperties props) {
        FilterRegistrationBean<SessionCryptoFilter> reg =
                new FilterRegistrationBean<>(new SessionCryptoFilter(crypto, props));
        reg.addUrlPatterns("/*");
        reg.setOrder(Ordered.HIGHEST_PRECEDENCE + 20);   // early, but after CORS/encoding filters
        reg.setName("vkpSessionCryptoFilter");
        return reg;
    }
}
