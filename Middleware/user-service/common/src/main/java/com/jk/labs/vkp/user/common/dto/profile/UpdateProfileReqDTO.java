package com.jk.labs.vkp.user.common.dto.profile;

import jakarta.validation.constraints.Size;
import lombok.AllArgsConstructor;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@NoArgsConstructor
@AllArgsConstructor
public class UpdateProfileReqDTO {

    // Populated by the controller from the path variable, not from the request body.
    private String userId;

    @Size(max = 100)
    private String firstName;

    @Size(max = 100)
    private String lastName;
}
