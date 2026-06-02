package com.jk.labs.vkp.user.service.mapper;

import com.jk.labs.vkp.user.common.dto.user.UserDTO;
import com.jk.labs.vkp.user.dao.entity.UserEntity;
import lombok.AccessLevel;
import lombok.NoArgsConstructor;

/** Maps {@link UserEntity} to {@link UserDTO}. Never exposes the password hash. */
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public final class UserMapper {

    public static UserDTO toDTO(UserEntity e) {
        if (e == null) {
            return null;
        }
        return UserDTO.builder()
                .userId(e.getUserId())
                .email(e.getEmail())
                .firstName(e.getFirstName())
                .lastName(e.getLastName())
                .role(e.getRole())
                .status(e.getStatus())
                .createdDt(e.getCreatedDt())
                .updatedDt(e.getUpdatedDt())
                .build();
    }
}
