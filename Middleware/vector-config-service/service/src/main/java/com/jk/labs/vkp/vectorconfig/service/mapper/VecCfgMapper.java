package com.jk.labs.vkp.vectorconfig.service.mapper;

import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.VecCfgDTO;
import com.jk.labs.vkp.vectorconfig.dao.entity.VecCfgEntity;
import lombok.AccessLevel;
import lombok.NoArgsConstructor;

/** Maps between {@link VecCfgEntity} and {@link VecCfgDTO}. */
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public final class VecCfgMapper {

    public static VecCfgDTO toDTO(VecCfgEntity e) {
        if (e == null) {
            return null;
        }
        return VecCfgDTO.builder()
                .vectorConfigId(e.getVectorConfigId())
                .companyId(e.getCompanyId())
                .companyResourceId(e.getCompanyResourceId())
                .vectorStoreType(e.getVectorStoreType())
                .vectorStoreName(e.getVectorStoreName())
                .collectionName(e.getCollectionName())
                .indexName(e.getIndexName())
                .embeddingModel(e.getEmbeddingModel())
                .isPrimary(e.getIsPrimary())
                .status(e.getStatus())
                .addlData(e.getAddlData())
                .createdDt(e.getCreatedDt())
                .updatedDt(e.getUpdatedDt())
                .createdBy(e.getCreatedBy())
                .updatedBy(e.getUpdatedBy())
                .build();
    }

    public static VecCfgEntity toEntity(VecCfgDTO d) {
        if (d == null) {
            return null;
        }
        return VecCfgEntity.builder()
                .vectorConfigId(d.getVectorConfigId())
                .companyId(d.getCompanyId())
                .companyResourceId(d.getCompanyResourceId())
                .vectorStoreType(d.getVectorStoreType())
                .vectorStoreName(d.getVectorStoreName())
                .collectionName(d.getCollectionName())
                .indexName(d.getIndexName())
                .embeddingModel(d.getEmbeddingModel())
                .isPrimary(d.getIsPrimary())
                .status(d.getStatus())
                .addlData(d.getAddlData())
                .createdDt(d.getCreatedDt())
                .updatedDt(d.getUpdatedDt())
                .createdBy(d.getCreatedBy())
                .updatedBy(d.getUpdatedBy())
                .build();
    }
}
