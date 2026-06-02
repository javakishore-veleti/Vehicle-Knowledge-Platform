package com.jk.labs.vkp.company.service;

import com.jk.labs.vkp.company.common.dto.company.CreateCompCtx;
import com.jk.labs.vkp.company.common.dto.company.CreateCompRespDTO;
import com.jk.labs.vkp.company.common.dto.company.CompDTO;
import com.jk.labs.vkp.company.common.dto.company.DeleteCompCtx;
import com.jk.labs.vkp.company.common.dto.company.DeleteCompRespDTO;
import com.jk.labs.vkp.company.common.dto.company.GetCompCtx;
import com.jk.labs.vkp.company.common.dto.company.GetCompRespDTO;
import com.jk.labs.vkp.company.common.dto.company.ListCompsCtx;
import com.jk.labs.vkp.company.common.dto.company.ListCompsRespDTO;
import com.jk.labs.vkp.company.common.dto.company.UpdateCompCtx;
import com.jk.labs.vkp.company.common.dto.company.UpdateCompRespDTO;
import com.jk.labs.vkp.company.common.enums.Status;
import com.jk.labs.vkp.company.common.error.ResourceNotFoundException;
import com.jk.labs.vkp.company.dao.entity.CompEntity;
import com.jk.labs.vkp.company.dao.repository.CompRepository;
import com.jk.labs.vkp.company.service.mapper.CompMapper;
import com.jk.labs.vkp.company.utils.AuditUtils;
import com.jk.labs.vkp.company.utils.IdGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;

/**
 * Business logic for company CRUD.
 *
 * Every method takes only its use case {@code Ctx}: it reads the request DTO from the
 * context and writes the response DTO back into the same context. No method declares
 * independent arguments.
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class CompService {

    private final CompRepository companyRepository;

    @Transactional
    public void create(CreateCompCtx ctx) {
        CompDTO in = ctx.getReqDTO().getCompany();
        Instant now = Instant.now();

        CompEntity entity = CompMapper.toEntity(in);
        entity.setCompanyId(IdGenerator.newId());
        entity.setStatus(in.getStatus() != null ? in.getStatus() : Status.DEFAULT);
        entity.setCreatedDt(now);
        entity.setUpdatedDt(now);
        entity.setCreatedBy(AuditUtils.actorOrDefault(in.getCreatedBy()));
        entity.setUpdatedBy(entity.getCreatedBy());

        CompEntity saved = companyRepository.save(entity);
        log.info("Created company {}", saved.getCompanyId());
        ctx.setRespDTO(new CreateCompRespDTO(CompMapper.toDTO(saved)));
    }

    @Transactional(readOnly = true)
    public void get(GetCompCtx ctx) {
        String id = ctx.getReqDTO().getCompanyId();
        CompEntity entity = companyRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Company not found: " + id));
        ctx.setRespDTO(new GetCompRespDTO(CompMapper.toDTO(entity)));
    }

    @Transactional(readOnly = true)
    public void list(ListCompsCtx ctx) {
        String status = ctx.getReqDTO() == null ? null : ctx.getReqDTO().getStatus();
        List<CompEntity> rows = (status == null || status.isBlank())
                ? companyRepository.findAll()
                : companyRepository.findByStatus(status);
        List<CompDTO> dtos = rows.stream().map(CompMapper::toDTO).toList();
        ctx.setRespDTO(new ListCompsRespDTO(dtos, dtos.size()));
    }

    @Transactional
    public void update(UpdateCompCtx ctx) {
        String id = ctx.getReqDTO().getCompanyId();
        CompDTO in = ctx.getReqDTO().getCompany();
        CompEntity entity = companyRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Company not found: " + id));

        if (in.getName() != null) {
            entity.setName(in.getName());
        }
        if (in.getDescription() != null) {
            entity.setDescription(in.getDescription());
        }
        if (in.getStatus() != null) {
            entity.setStatus(in.getStatus());
        }
        entity.setUpdatedDt(Instant.now());
        entity.setUpdatedBy(AuditUtils.actorOrDefault(in.getUpdatedBy()));

        CompEntity saved = companyRepository.save(entity);
        log.info("Updated company {}", saved.getCompanyId());
        ctx.setRespDTO(new UpdateCompRespDTO(CompMapper.toDTO(saved)));
    }

    @Transactional
    public void delete(DeleteCompCtx ctx) {
        String id = ctx.getReqDTO().getCompanyId();
        if (!companyRepository.existsById(id)) {
            throw new ResourceNotFoundException("Company not found: " + id);
        }
        companyRepository.deleteById(id);
        log.info("Deleted company {}", id);
        ctx.setRespDTO(new DeleteCompRespDTO(id, true));
    }
}
