package com.jk.labs.vkp.datacollection.service.mapper;

import com.jk.labs.vkp.datacollection.common.dto.graph.ResourceGraphNodeDTO;
import com.jk.labs.vkp.datacollection.dao.entity.ResourceGraphNodeEntity;
import lombok.AccessLevel;
import lombok.NoArgsConstructor;

/** Maps {@link ResourceGraphNodeEntity} to {@link ResourceGraphNodeDTO}. */
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public final class ResourceGraphNodeMapper {

    public static ResourceGraphNodeDTO toDTO(ResourceGraphNodeEntity e) {
        if (e == null) {
            return null;
        }
        return ResourceGraphNodeDTO.builder()
                .resourceGraphId(e.getResourceGraphId())
                .companyId(e.getCompanyId())
                .companyResourceId(e.getCompanyResourceId())
                .parentResourceGraphId(e.getParentResourceGraphId())
                .resourceUrl(e.getResourceUrl())
                .resourceType(e.getResourceType())
                .parentResourceType(e.getParentResourceType())
                .crawlStatus(e.getCrawlStatus())
                .status(e.getStatus())
                .createdDt(e.getCreatedDt())
                .updatedDt(e.getUpdatedDt())
                .build();
    }
}
