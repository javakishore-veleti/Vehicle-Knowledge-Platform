package com.jk.labs.vkp.user.common.dto.profile;

import com.jk.labs.vkp.user.common.dto.user.UserDTO;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GetProfileRespDTO {

    private UserDTO user;
}
