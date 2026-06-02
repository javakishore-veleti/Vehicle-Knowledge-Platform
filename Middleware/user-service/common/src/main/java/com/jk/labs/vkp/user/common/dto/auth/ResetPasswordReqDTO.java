package com.jk.labs.vkp.user.common.dto.auth;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ResetPasswordReqDTO {

    @NotBlank
    private String resetToken;

    @NotBlank
    @Size(min = 8, max = 100)
    private String newPassword;
}
