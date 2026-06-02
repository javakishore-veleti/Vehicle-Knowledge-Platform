package com.jk.labs.vkp.ingestion.service.mapper;

import com.jk.labs.vkp.ingestion.common.dto.content.ContentDTO;
import com.jk.labs.vkp.ingestion.dao.entity.ContentEntity;
import lombok.AccessLevel;
import lombok.NoArgsConstructor;

/** Maps {@link ContentEntity} to {@link ContentDTO} (omits the full text body). */
@NoArgsConstructor(access = AccessLevel.PRIVATE)
public final class ContentMapper {

    public static ContentDTO toDTO(ContentEntity e) {
        if (e == null) {
            return null;
        }
        return ContentDTO.builder()
                .contentId(e.getContentId())
                .companyId(e.getCompanyId())
                .companyResourceId(e.getCompanyResourceId())
                .resourceGraphId(e.getResourceGraphId())
                .sourceUrl(e.getSourceUrl())
                .title(e.getTitle())
                .contentHash(e.getContentHash())
                .textLength(e.getCleanText() == null ? 0 : e.getCleanText().length())
                .crawlStatus(e.getCrawlStatus())
                .embeddingStatus(e.getEmbeddingStatus())
                .createdDt(e.getCreatedDt())
                .updatedDt(e.getUpdatedDt())
                .build();
    }
}
