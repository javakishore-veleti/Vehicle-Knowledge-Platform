package com.jk.labs.vkp.vectorconfig.service;

import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.CreateVecCfgCtx;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.CreateVecCfgRespDTO;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.DeleteVecCfgCtx;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.DeleteVecCfgRespDTO;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.GetVecCfgCtx;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.GetVecCfgRespDTO;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.ListVecCfgsCtx;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.ListVecCfgsReqDTO;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.ListVecCfgsRespDTO;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.UpdateVecCfgCtx;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.UpdateVecCfgRespDTO;
import com.jk.labs.vkp.vectorconfig.common.dto.vectorconfig.VecCfgDTO;
import com.jk.labs.vkp.vectorconfig.common.enums.Status;
import com.jk.labs.vkp.vectorconfig.common.enums.VectorStoreType;
import com.jk.labs.vkp.vectorconfig.common.error.InvalidConfigException;
import com.jk.labs.vkp.vectorconfig.common.error.ResourceNotFoundException;
import com.jk.labs.vkp.vectorconfig.dao.entity.VecCfgEntity;
import com.jk.labs.vkp.vectorconfig.dao.repository.VecCfgRepository;
import com.jk.labs.vkp.vectorconfig.service.mapper.VecCfgMapper;
import com.jk.labs.vkp.vectorconfig.utils.AuditUtils;
import com.jk.labs.vkp.vectorconfig.utils.IdGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;

/**
 * Business logic for vector-config CRUD - the configuration-driven vector-store selection
 * (architectural rule #3). A company resource may have many configs (one per store); at most
 * one is marked primary. Every method takes only its use case {@code Ctx}.
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class VecCfgService {

    private final VecCfgRepository repository;

    @Transactional
    public void create(CreateVecCfgCtx ctx) {
        String companyResourceId = ctx.getReqDTO().getCompanyResourceId();
        VecCfgDTO in = ctx.getReqDTO().getVectorConfig();
        validateStoreType(in.getVectorStoreType());
        Instant now = Instant.now();

        VecCfgEntity entity = VecCfgMapper.toEntity(in);
        entity.setVectorConfigId(IdGenerator.newId());
        entity.setCompanyResourceId(companyResourceId);
        entity.setVectorStoreType(VectorStoreType.normalize(in.getVectorStoreType()));
        entity.setStatus(in.getStatus() != null ? in.getStatus() : Status.DEFAULT);
        entity.setIsPrimary(Boolean.TRUE.equals(in.getIsPrimary()));
        entity.setCreatedDt(now);
        entity.setUpdatedDt(now);
        entity.setCreatedBy(AuditUtils.actorOrDefault(in.getCreatedBy()));
        entity.setUpdatedBy(entity.getCreatedBy());

        if (Boolean.TRUE.equals(entity.getIsPrimary())) {
            demoteOtherPrimaries(companyResourceId, entity.getVectorConfigId());
        }

        VecCfgEntity saved = repository.save(entity);
        log.info("Created vector config {} ({}) for resource {} primary={}",
                saved.getVectorConfigId(), saved.getVectorStoreType(),
                companyResourceId, saved.getIsPrimary());
        ctx.setRespDTO(new CreateVecCfgRespDTO(VecCfgMapper.toDTO(saved)));
    }

    @Transactional(readOnly = true)
    public void get(GetVecCfgCtx ctx) {
        String id = ctx.getReqDTO().getVectorConfigId();
        VecCfgEntity entity = repository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Vector config not found: " + id));
        ctx.setRespDTO(new GetVecCfgRespDTO(VecCfgMapper.toDTO(entity)));
    }

    @Transactional(readOnly = true)
    public void list(ListVecCfgsCtx ctx) {
        ListVecCfgsReqDTO req = ctx.getReqDTO() == null ? new ListVecCfgsReqDTO() : ctx.getReqDTO();
        List<VecCfgEntity> rows;
        if (req.getCompanyResourceId() != null && !req.getCompanyResourceId().isBlank()) {
            rows = repository.findByCompanyResourceId(req.getCompanyResourceId());
        } else if (req.getCompanyId() != null && !req.getCompanyId().isBlank()) {
            rows = repository.findByCompanyId(req.getCompanyId());
        } else if (req.getStatus() != null && !req.getStatus().isBlank()) {
            rows = repository.findByStatus(req.getStatus());
        } else {
            rows = repository.findAll();
        }
        if (req.getStatus() != null && !req.getStatus().isBlank()) {
            rows = rows.stream().filter(r -> req.getStatus().equalsIgnoreCase(r.getStatus())).toList();
        }
        List<VecCfgDTO> dtos = rows.stream().map(VecCfgMapper::toDTO).toList();
        ctx.setRespDTO(new ListVecCfgsRespDTO(dtos, dtos.size()));
    }

    @Transactional
    public void update(UpdateVecCfgCtx ctx) {
        String id = ctx.getReqDTO().getVectorConfigId();
        VecCfgDTO in = ctx.getReqDTO().getVectorConfig();
        VecCfgEntity entity = repository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Vector config not found: " + id));

        if (in.getVectorStoreType() != null) {
            validateStoreType(in.getVectorStoreType());
            entity.setVectorStoreType(VectorStoreType.normalize(in.getVectorStoreType()));
        }
        if (in.getVectorStoreName() != null) {
            entity.setVectorStoreName(in.getVectorStoreName());
        }
        if (in.getCollectionName() != null) {
            entity.setCollectionName(in.getCollectionName());
        }
        if (in.getIndexName() != null) {
            entity.setIndexName(in.getIndexName());
        }
        if (in.getEmbeddingModel() != null) {
            entity.setEmbeddingModel(in.getEmbeddingModel());
        }
        if (in.getStatus() != null) {
            entity.setStatus(in.getStatus());
        }
        if (in.getAddlData() != null) {
            entity.setAddlData(in.getAddlData());
        }
        if (in.getIsPrimary() != null) {
            entity.setIsPrimary(in.getIsPrimary());
            if (Boolean.TRUE.equals(in.getIsPrimary())) {
                demoteOtherPrimaries(entity.getCompanyResourceId(), entity.getVectorConfigId());
            }
        }
        entity.setUpdatedDt(Instant.now());
        entity.setUpdatedBy(AuditUtils.actorOrDefault(in.getUpdatedBy()));

        VecCfgEntity saved = repository.save(entity);
        log.info("Updated vector config {}", saved.getVectorConfigId());
        ctx.setRespDTO(new UpdateVecCfgRespDTO(VecCfgMapper.toDTO(saved)));
    }

    @Transactional
    public void delete(DeleteVecCfgCtx ctx) {
        String id = ctx.getReqDTO().getVectorConfigId();
        if (!repository.existsById(id)) {
            throw new ResourceNotFoundException("Vector config not found: " + id);
        }
        repository.deleteById(id);
        log.info("Deleted vector config {}", id);
        ctx.setRespDTO(new DeleteVecCfgRespDTO(id, true));
    }

    /** Enforces a single primary store per resource: clears is_primary on every sibling. */
    private void demoteOtherPrimaries(String companyResourceId, String keepId) {
        if (companyResourceId == null) {
            return;
        }
        for (VecCfgEntity other : repository.findByCompanyResourceIdAndIsPrimaryTrue(companyResourceId)) {
            if (!other.getVectorConfigId().equals(keepId)) {
                other.setIsPrimary(false);
                other.setUpdatedDt(Instant.now());
                repository.save(other);
                log.info("Demoted previous primary vector config {} for resource {}",
                        other.getVectorConfigId(), companyResourceId);
            }
        }
    }

    private void validateStoreType(String storeType) {
        if (!VectorStoreType.isValid(storeType)) {
            throw new InvalidConfigException("Unsupported vectorStoreType: " + storeType
                    + " (allowed: mongodb, chromadb, pgvector, weaviate, pinecone)");
        }
    }
}
