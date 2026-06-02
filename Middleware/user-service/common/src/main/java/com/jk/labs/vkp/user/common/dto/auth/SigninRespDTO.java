package com.jk.labs.vkp.user.common.dto.auth;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SigninRespDTO {

    private String token;
    private String tokenType;
    private String userId;
    private String email;
    private Instant expiresAt;
}
