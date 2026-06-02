package com.jk.labs.vkp.company.service.mapper;

import com.jk.labs.vkp.company.common.dto.company.CompDTO;
import com.jk.labs.vkp.company.dao.entity.CompEntity;
import lombok.AccessLevel;
import lombok.NoArgsConstructor;

/** Maps between {@link CompEntity} and {@link CompDTO}. */
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public final class CompMapper {

    public static CompDTO toDTO(CompEntity e) {
        if (e == null) {
            return null;
        }
        return CompDTO.builder()
                .companyId(e.getCompanyId())
                .name(e.getName())
                .description(e.getDescription())
                .status(e.getStatus())
                .createdDt(e.getCreatedDt())
                .updatedDt(e.getUpdatedDt())
                .createdBy(e.getCreatedBy())
                .updatedBy(e.getUpdatedBy())
                .build();
    }

    public static CompEntity toEntity(CompDTO d) {
        if (d == null) {
            return null;
        }
        return CompEntity.builder()
                .companyId(d.getCompanyId())
                .name(d.getName())
                .description(d.getDescription())
                .status(d.getStatus())
                .createdDt(d.getCreatedDt())
                .updatedDt(d.getUpdatedDt())
                .createdBy(d.getCreatedBy())
                .updatedBy(d.getUpdatedBy())
                .build();
    }
}
