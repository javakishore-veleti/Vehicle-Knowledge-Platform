package com.jk.labs.vkp.rbac;

import org.springframework.boot.autoconfigure.AutoConfiguration;
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.context.properties.EnableConfigurationProperties;
import org.springframework.boot.web.servlet.FilterRegistrationBean;
import org.springframework.context.annotation.Bean;
import org.springframework.core.Ordered;

/**
 * Auto-registers the {@link JwtRbacFilter} (and its {@link JwtService}) in any service that adds
 * this library. Active unless {@code vkp.jwt.enabled=false}. Ordered just after the session-crypto
 * filter so the session context is already established when RBAC runs.
 */
@AutoConfiguration
@EnableConfigurationProperties(JwtRbacProperties.class)
@ConditionalOnProperty(prefix = "vkp.jwt", name = "enabled", matchIfMissing = true)
public class JwtRbacAutoConfiguration {

    @Bean
    @ConditionalOnMissingBean
    public JwtService vkpJwtService(JwtRbacProperties props) {
        return new JwtService(props.getSecret(), props.getRoleClaim());
    }

    @Bean
    public FilterRegistrationBean<JwtRbacFilter> vkpJwtRbacFilter(JwtService jwt, JwtRbacProperties props) {
        FilterRegistrationBean<JwtRbacFilter> reg =
                new FilterRegistrationBean<>(new JwtRbacFilter(jwt, props));
        reg.addUrlPatterns("/*");
        reg.setOrder(Ordered.HIGHEST_PRECEDENCE + 30);   // after vkpSessionCryptoFilter (+20)
        reg.setName("vkpJwtRbacFilter");
        return reg;
    }
}
