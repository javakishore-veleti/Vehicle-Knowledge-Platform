package com.jk.labs.vkp.customer.service.mapper;

import com.jk.labs.vkp.customer.common.dto.resource.CustResourceDTO;
import com.jk.labs.vkp.customer.dao.entity.CustResourceEntity;
import lombok.AccessLevel;
import lombok.NoArgsConstructor;

/** Maps between {@link CustResourceEntity} and {@link CustResourceDTO}. */
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public final class CustResourceMapper {

    public static CustResourceDTO toDTO(CustResourceEntity e) {
        if (e == null) {
            return null;
        }
        return CustResourceDTO.builder()
                .customerResourceId(e.getCustomerResourceId())
                .customerId(e.getCustomerId())
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

    public static CustResourceEntity toEntity(CustResourceDTO d) {
        if (d == null) {
            return null;
        }
        return CustResourceEntity.builder()
                .customerResourceId(d.getCustomerResourceId())
                .customerId(d.getCustomerId())
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
