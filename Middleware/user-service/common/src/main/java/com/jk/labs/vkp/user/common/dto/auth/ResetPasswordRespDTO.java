package com.jk.labs.vkp.user.common.dto.auth;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ResetPasswordRespDTO {

    private boolean success;
    private String message;
}
