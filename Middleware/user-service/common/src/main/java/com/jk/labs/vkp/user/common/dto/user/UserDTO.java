package com.jk.labs.vkp.user.common.dto.user;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.time.Instant;

/**
 * Public wire shape of a portal end-user. NEVER carries the password hash.
 * Backed by the {@code customer_users} collection/table in the VKP data model.
 */
@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class UserDTO {

    private String userId;
    private String email;
    private String firstName;
    private String lastName;
    private String role;
    private String status;
    private Instant createdDt;
    private Instant updatedDt;
}
