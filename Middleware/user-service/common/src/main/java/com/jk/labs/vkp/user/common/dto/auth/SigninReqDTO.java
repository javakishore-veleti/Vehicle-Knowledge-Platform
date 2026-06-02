package com.jk.labs.vkp.user.common.dto.auth;

import jakarta.validation.constraints.Email;
import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SigninReqDTO {

    @Email
    @NotBlank
    private String email;

    @NotBlank
    private String password;
}
