package com.jk.labs.vkp.company.service.mapper;

import com.jk.labs.vkp.company.common.dto.resource.CompResourceDTO;
import com.jk.labs.vkp.company.dao.entity.CompResourceEntity;
import lombok.AccessLevel;
import lombok.NoArgsConstructor;

/** Maps between {@link CompResourceEntity} and {@link CompResourceDTO}. */
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public final class CompResourceMapper {

    public static CompResourceDTO toDTO(CompResourceEntity e) {
        if (e == null) {
            return null;
        }
        return CompResourceDTO.builder()
                .companyResourceId(e.getCompanyResourceId())
                .companyId(e.getCompanyId())
                .resourceName(e.getResourceName())
                .resourceLink(e.getResourceLink())
                .resourceType(e.getResourceType())
                .status(e.getStatus())
                .createdDt(e.getCreatedDt())
                .updatedDt(e.getUpdatedDt())
                .createdBy(e.getCreatedBy())
                .updatedBy(e.getUpdatedBy())
                .build();
    }

    public static CompResourceEntity toEntity(CompResourceDTO d) {
        if (d == null) {
            return null;
        }
        return CompResourceEntity.builder()
                .companyResourceId(d.getCompanyResourceId())
                .companyId(d.getCompanyId())
                .resourceName(d.getResourceName())
                .resourceLink(d.getResourceLink())
                .resourceType(d.getResourceType())
                .status(d.getStatus())
                .createdDt(d.getCreatedDt())
                .updatedDt(d.getUpdatedDt())
                .createdBy(d.getCreatedBy())
                .updatedBy(d.getUpdatedBy())
                .build();
    }
}
