package com.jk.labs.vkp.user.common.dto.auth;

import com.jk.labs.vkp.user.common.dto.user.UserDTO;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class SignupRespDTO {

    private UserDTO user;
}
