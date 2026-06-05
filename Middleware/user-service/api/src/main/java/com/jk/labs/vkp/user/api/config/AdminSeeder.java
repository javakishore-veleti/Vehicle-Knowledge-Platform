package com.jk.labs.vkp.user.api.config;

import com.jk.labs.vkp.user.common.enums.Role;
import com.jk.labs.vkp.user.common.enums.Status;
import com.jk.labs.vkp.user.dao.entity.UserEntity;
import com.jk.labs.vkp.user.dao.repository.UserRepository;
import com.jk.labs.vkp.user.utils.AuditUtils;
import com.jk.labs.vkp.user.utils.IdGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.boot.context.event.ApplicationReadyEvent;
import org.springframework.context.event.EventListener;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Component;

import java.time.Instant;

/**
 * Seeds a single ADMIN user on startup if one doesn't exist, so the admin-portal can sign in and
 * obtain an ADMIN-role JWT for the /admin/** services (enforced by vkp-jwt-rbac). Idempotent.
 * Credentials are dev defaults (override via VKP_ADMIN_EMAIL / VKP_ADMIN_PASSWORD).
 */
@Component
@Slf4j
@RequiredArgsConstructor
public class AdminSeeder {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;

    @EventListener(ApplicationReadyEvent.class)
    public void seedAdmin() {
        String email = normalize(System.getenv().getOrDefault("VKP_ADMIN_EMAIL", "admin@vkp.local"));
        String password = System.getenv().getOrDefault("VKP_ADMIN_PASSWORD", "admin12345");
        if (userRepository.existsByEmail(email)) {
            log.info("Admin user already present ({}), skipping seed", email);
            return;
        }
        Instant now = Instant.now();
        userRepository.save(UserEntity.builder()
                .userId(IdGenerator.newId())
                .email(email)
                .passwordHash(passwordEncoder.encode(password))
                .firstName("VKP")
                .lastName("Admin")
                .role(Role.ADMIN.name())
                .status(Status.ACTIVE.name())
                .createdDt(now).updatedDt(now)
                .createdBy(AuditUtils.SYSTEM_ACTOR).updatedBy(AuditUtils.SYSTEM_ACTOR)
                .build());
        log.info("Seeded ADMIN user {} (override via VKP_ADMIN_EMAIL / VKP_ADMIN_PASSWORD)", email);
    }

    private static String normalize(String email) {
        return email == null ? null : email.trim().toLowerCase();
    }
}
