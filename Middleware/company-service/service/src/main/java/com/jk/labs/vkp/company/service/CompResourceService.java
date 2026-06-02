package com.jk.labs.vkp.company.service;

import com.jk.labs.vkp.company.common.dto.resource.CreateCompResourceCtx;
import com.jk.labs.vkp.company.common.dto.resource.CreateCompResourceRespDTO;
import com.jk.labs.vkp.company.common.dto.resource.CompResourceDTO;
import com.jk.labs.vkp.company.common.dto.resource.DeleteCompResourceCtx;
import com.jk.labs.vkp.company.common.dto.resource.DeleteCompResourceRespDTO;
import com.jk.labs.vkp.company.common.dto.resource.ListCompResourcesCtx;
import com.jk.labs.vkp.company.common.dto.resource.ListCompResourcesRespDTO;
import com.jk.labs.vkp.company.common.dto.resource.UpdateCompResourceCtx;
import com.jk.labs.vkp.company.common.dto.resource.UpdateCompResourceRespDTO;
import com.jk.labs.vkp.company.common.enums.Status;
import com.jk.labs.vkp.company.common.error.ResourceNotFoundException;
import com.jk.labs.vkp.company.dao.entity.CompResourceEntity;
import com.jk.labs.vkp.company.dao.repository.CompRepository;
import com.jk.labs.vkp.company.dao.repository.CompResourceRepository;
import com.jk.labs.vkp.company.service.mapper.CompResourceMapper;
import com.jk.labs.vkp.company.utils.AuditUtils;
import com.jk.labs.vkp.company.utils.IdGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;

/**
 * Business logic for company resource CRUD (a related table of company).
 *
 * Every method takes only its use case {@code Ctx}.
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class CompResourceService {

    private final CompResourceRepository resourceRepository;
    private final CompRepository companyRepository;

    @Transactional
    public void create(CreateCompResourceCtx ctx) {
        String companyId = ctx.getReqDTO().getCompanyId();
        ensureCompanyExists(companyId);

        CompResourceDTO in = ctx.getReqDTO().getResource();
        Instant now = Instant.now();

        CompResourceEntity entity = CompResourceMapper.toEntity(in);
        entity.setCompanyResourceId(IdGenerator.newId());
        entity.setCompanyId(companyId);
        entity.setStatus(in.getStatus() != null ? in.getStatus() : Status.DEFAULT);
        entity.setCreatedDt(now);
        entity.setUpdatedDt(now);
        entity.setCreatedBy(AuditUtils.actorOrDefault(in.getCreatedBy()));
        entity.setUpdatedBy(entity.getCreatedBy());

        CompResourceEntity saved = resourceRepository.save(entity);
        log.info("Created company resource {} for company {}", saved.getCompanyResourceId(), companyId);
        ctx.setRespDTO(new CreateCompResourceRespDTO(CompResourceMapper.toDTO(saved)));
    }

    @Transactional(readOnly = true)
    public void list(ListCompResourcesCtx ctx) {
        String companyId = ctx.getReqDTO().getCompanyId();
        ensureCompanyExists(companyId);
        List<CompResourceEntity> rows = resourceRepository.findByCompanyId(companyId);
        List<CompResourceDTO> dtos = rows.stream().map(CompResourceMapper::toDTO).toList();
        ctx.setRespDTO(new ListCompResourcesRespDTO(dtos, dtos.size()));
    }

    @Transactional
    public void update(UpdateCompResourceCtx ctx) {
        String companyId = ctx.getReqDTO().getCompanyId();
        String resourceId = ctx.getReqDTO().getResourceId();
        CompResourceEntity entity = resourceRepository
                .findByCompanyResourceIdAndCompanyId(resourceId, companyId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Company resource not found: " + resourceId + " for company " + companyId));

        CompResourceDTO in = ctx.getReqDTO().getResource();
        if (in.getResourceName() != null) {
            entity.setResourceName(in.getResourceName());
        }
        if (in.getResourceLink() != null) {
            entity.setResourceLink(in.getResourceLink());
        }
        if (in.getResourceType() != null) {
            entity.setResourceType(in.getResourceType());
        }
        if (in.getStatus() != null) {
            entity.setStatus(in.getStatus());
        }
        entity.setUpdatedDt(Instant.now());
        entity.setUpdatedBy(AuditUtils.actorOrDefault(in.getUpdatedBy()));

        CompResourceEntity saved = resourceRepository.save(entity);
        log.info("Updated company resource {}", saved.getCompanyResourceId());
        ctx.setRespDTO(new UpdateCompResourceRespDTO(CompResourceMapper.toDTO(saved)));
    }

    @Transactional
    public void delete(DeleteCompResourceCtx ctx) {
        String companyId = ctx.getReqDTO().getCompanyId();
        String resourceId = ctx.getReqDTO().getResourceId();
        CompResourceEntity entity = resourceRepository
                .findByCompanyResourceIdAndCompanyId(resourceId, companyId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Company resource not found: " + resourceId + " for company " + companyId));
        resourceRepository.delete(entity);
        log.info("Deleted company resource {}", resourceId);
        ctx.setRespDTO(new DeleteCompResourceRespDTO(resourceId, true));
    }

    private void ensureCompanyExists(String companyId) {
        if (!companyRepository.existsById(companyId)) {
            throw new ResourceNotFoundException("Company not found: " + companyId);
        }
    }
}
