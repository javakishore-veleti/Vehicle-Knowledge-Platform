package com.jk.labs.vkp.user.common.dto.auth;

import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class ForgotPasswordRespDTO {

    private String message;

    /**
     * Reset token. In production this is emailed to the user, not returned in the response;
     * it is surfaced here only while email delivery is stubbed (dev convenience).
     */
    private String resetToken;
}
