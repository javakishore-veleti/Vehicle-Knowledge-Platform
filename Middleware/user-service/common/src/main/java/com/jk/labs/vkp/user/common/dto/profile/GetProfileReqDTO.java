package com.jk.labs.vkp.user.common.dto.profile;

import jakarta.validation.constraints.NotBlank;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class GetProfileReqDTO {

    @NotBlank
    private String userId;
}
