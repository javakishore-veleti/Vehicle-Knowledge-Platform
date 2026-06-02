package com.jk.labs.vkp.user.service;

import com.jk.labs.vkp.user.common.dto.auth.ForgotPasswordCtx;
import com.jk.labs.vkp.user.common.dto.auth.ForgotPasswordRespDTO;
import com.jk.labs.vkp.user.common.dto.auth.ResetPasswordCtx;
import com.jk.labs.vkp.user.common.dto.auth.ResetPasswordReqDTO;
import com.jk.labs.vkp.user.common.dto.auth.ResetPasswordRespDTO;
import com.jk.labs.vkp.user.common.dto.auth.SigninCtx;
import com.jk.labs.vkp.user.common.dto.auth.SigninReqDTO;
import com.jk.labs.vkp.user.common.dto.auth.SigninRespDTO;
import com.jk.labs.vkp.user.common.dto.auth.SignupCtx;
import com.jk.labs.vkp.user.common.dto.auth.SignupReqDTO;
import com.jk.labs.vkp.user.common.dto.auth.SignupRespDTO;
import com.jk.labs.vkp.user.common.dto.profile.GetProfileCtx;
import com.jk.labs.vkp.user.common.dto.profile.GetProfileRespDTO;
import com.jk.labs.vkp.user.common.dto.profile.UpdateProfileCtx;
import com.jk.labs.vkp.user.common.dto.profile.UpdateProfileReqDTO;
import com.jk.labs.vkp.user.common.dto.profile.UpdateProfileRespDTO;
import com.jk.labs.vkp.user.common.enums.Role;
import com.jk.labs.vkp.user.common.enums.Status;
import com.jk.labs.vkp.user.common.error.EmailAlreadyExistsException;
import com.jk.labs.vkp.user.common.error.ResourceNotFoundException;
import com.jk.labs.vkp.user.common.error.UnauthorizedException;
import com.jk.labs.vkp.user.dao.entity.UserEntity;
import com.jk.labs.vkp.user.dao.repository.UserRepository;
import com.jk.labs.vkp.user.service.mapper.UserMapper;
import com.jk.labs.vkp.user.utils.AuditUtils;
import com.jk.labs.vkp.user.utils.IdGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.time.temporal.ChronoUnit;

/**
 * Business logic for user signup, authentication, password reset, and profile.
 * Every method takes only its use case {@code Ctx}.
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class UserService {

    private static final long RESET_TOKEN_TTL_MINUTES = 30;

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final AuthTokenService authTokenService;

    @Transactional
    public void signup(SignupCtx ctx) {
        SignupReqDTO req = ctx.getReqDTO();
        String email = normalize(req.getEmail());
        if (userRepository.existsByEmail(email)) {
            throw new EmailAlreadyExistsException("Email already registered: " + email);
        }
        Instant now = Instant.now();
        UserEntity entity = UserEntity.builder()
                .userId(IdGenerator.newId())
                .email(email)
                .passwordHash(passwordEncoder.encode(req.getPassword()))
                .firstName(req.getFirstName())
                .lastName(req.getLastName())
                .role(Role.DEFAULT)
                .status(Status.DEFAULT)
                .createdDt(now)
                .updatedDt(now)
                .createdBy(AuditUtils.SYSTEM_ACTOR)
                .updatedBy(AuditUtils.SYSTEM_ACTOR)
                .build();
        UserEntity saved = userRepository.save(entity);
        log.info("Registered user {} ({})", saved.getUserId(), email);
        ctx.setRespDTO(new SignupRespDTO(UserMapper.toDTO(saved)));
    }

    @Transactional(readOnly = true)
    public void signin(SigninCtx ctx) {
        SigninReqDTO req = ctx.getReqDTO();
        UserEntity entity = userRepository.findByEmail(normalize(req.getEmail()))
                .orElseThrow(() -> new UnauthorizedException("Invalid email or password"));
        if (!passwordEncoder.matches(req.getPassword(), entity.getPasswordHash())) {
            throw new UnauthorizedException("Invalid email or password");
        }
        AuthTokenService.IssuedToken token = authTokenService.issue(entity.getUserId(), entity.getEmail());
        ctx.setRespDTO(new SigninRespDTO(token.token(), "Bearer",
                entity.getUserId(), entity.getEmail(), token.expiresAt()));
    }

    @Transactional
    public void forgotPassword(ForgotPasswordCtx ctx) {
        String email = normalize(ctx.getReqDTO().getEmail());
        UserEntity entity = userRepository.findByEmail(email)
                .orElseThrow(() -> new ResourceNotFoundException("No user with email: " + email));
        String token = IdGenerator.newId();
        entity.setResetToken(token);
        entity.setResetTokenExpiry(Instant.now().plus(RESET_TOKEN_TTL_MINUTES, ChronoUnit.MINUTES));
        entity.setUpdatedDt(Instant.now());
        userRepository.save(entity);
        // TODO: deliver the reset token via email. Stubbed here (returned in the response for dev).
        log.info("Password reset requested for {} (email delivery stubbed)", email);
        ctx.setRespDTO(new ForgotPasswordRespDTO("Password reset token generated", token));
    }

    @Transactional
    public void resetPassword(ResetPasswordCtx ctx) {
        ResetPasswordReqDTO req = ctx.getReqDTO();
        UserEntity entity = userRepository.findByResetToken(req.getResetToken())
                .orElseThrow(() -> new UnauthorizedException("Invalid reset token"));
        if (entity.getResetTokenExpiry() == null || entity.getResetTokenExpiry().isBefore(Instant.now())) {
            throw new UnauthorizedException("Reset token expired");
        }
        entity.setPasswordHash(passwordEncoder.encode(req.getNewPassword()));
        entity.setResetToken(null);
        entity.setResetTokenExpiry(null);
        entity.setUpdatedDt(Instant.now());
        userRepository.save(entity);
        log.info("Password reset for user {}", entity.getUserId());
        ctx.setRespDTO(new ResetPasswordRespDTO(true, "Password updated"));
    }

    @Transactional(readOnly = true)
    public void getProfile(GetProfileCtx ctx) {
        String userId = ctx.getReqDTO().getUserId();
        UserEntity entity = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User not found: " + userId));
        ctx.setRespDTO(new GetProfileRespDTO(UserMapper.toDTO(entity)));
    }

    @Transactional
    public void updateProfile(UpdateProfileCtx ctx) {
        UpdateProfileReqDTO req = ctx.getReqDTO();
        UserEntity entity = userRepository.findById(req.getUserId())
                .orElseThrow(() -> new ResourceNotFoundException("User not found: " + req.getUserId()));
        if (req.getFirstName() != null) {
            entity.setFirstName(req.getFirstName());
        }
        if (req.getLastName() != null) {
            entity.setLastName(req.getLastName());
        }
        entity.setUpdatedDt(Instant.now());
        userRepository.save(entity);
        ctx.setRespDTO(new UpdateProfileRespDTO(UserMapper.toDTO(entity)));
    }

    private static String normalize(String email) {
        return email == null ? null : email.trim().toLowerCase();
    }
}
