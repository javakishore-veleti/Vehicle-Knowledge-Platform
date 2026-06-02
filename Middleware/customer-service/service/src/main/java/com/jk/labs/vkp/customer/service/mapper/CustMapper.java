package com.jk.labs.vkp.customer.service.mapper;

import com.jk.labs.vkp.customer.common.dto.customer.CustDTO;
import com.jk.labs.vkp.customer.dao.entity.CustEntity;
import lombok.AccessLevel;
import lombok.NoArgsConstructor;

/** Maps between {@link CustEntity} and {@link CustDTO}. */
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public final class CustMapper {

    public static CustDTO toDTO(CustEntity e) {
        if (e == null) {
            return null;
        }
        return CustDTO.builder()
                .customerId(e.getCustomerId())
                .name(e.getName())
                .description(e.getDescription())
                .status(e.getStatus())
                .createdDt(e.getCreatedDt())
                .updatedDt(e.getUpdatedDt())
                .createdBy(e.getCreatedBy())
                .updatedBy(e.getUpdatedBy())
                .build();
    }

    public static CustEntity toEntity(CustDTO d) {
        if (d == null) {
            return null;
        }
        return CustEntity.builder()
                .customerId(d.getCustomerId())
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
