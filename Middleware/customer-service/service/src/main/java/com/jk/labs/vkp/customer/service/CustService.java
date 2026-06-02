package com.jk.labs.vkp.customer.service;

import com.jk.labs.vkp.customer.common.dto.customer.CreateCustCtx;
import com.jk.labs.vkp.customer.common.dto.customer.CreateCustRespDTO;
import com.jk.labs.vkp.customer.common.dto.customer.CustDTO;
import com.jk.labs.vkp.customer.common.dto.customer.DeleteCustCtx;
import com.jk.labs.vkp.customer.common.dto.customer.DeleteCustRespDTO;
import com.jk.labs.vkp.customer.common.dto.customer.GetCustCtx;
import com.jk.labs.vkp.customer.common.dto.customer.GetCustRespDTO;
import com.jk.labs.vkp.customer.common.dto.customer.ListCustsCtx;
import com.jk.labs.vkp.customer.common.dto.customer.ListCustsRespDTO;
import com.jk.labs.vkp.customer.common.dto.customer.UpdateCustCtx;
import com.jk.labs.vkp.customer.common.dto.customer.UpdateCustRespDTO;
import com.jk.labs.vkp.customer.common.enums.Status;
import com.jk.labs.vkp.customer.common.error.ResourceNotFoundException;
import com.jk.labs.vkp.customer.dao.entity.CustEntity;
import com.jk.labs.vkp.customer.dao.repository.CustRepository;
import com.jk.labs.vkp.customer.service.mapper.CustMapper;
import com.jk.labs.vkp.customer.utils.AuditUtils;
import com.jk.labs.vkp.customer.utils.IdGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;

/**
 * Business logic for customer CRUD.
 *
 * Every method takes only its use case {@code Ctx}: it reads the request DTO from the
 * context and writes the response DTO back into the same context. No method declares
 * independent arguments.
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class CustService {

    private final CustRepository customerRepository;

    @Transactional
    public void create(CreateCustCtx ctx) {
        CustDTO in = ctx.getReqDTO().getCustomer();
        Instant now = Instant.now();

        CustEntity entity = CustMapper.toEntity(in);
        entity.setCustomerId(IdGenerator.newId());
        entity.setStatus(in.getStatus() != null ? in.getStatus() : Status.DEFAULT);
        entity.setCreatedDt(now);
        entity.setUpdatedDt(now);
        entity.setCreatedBy(AuditUtils.actorOrDefault(in.getCreatedBy()));
        entity.setUpdatedBy(entity.getCreatedBy());

        CustEntity saved = customerRepository.save(entity);
        log.info("Created customer {}", saved.getCustomerId());
        ctx.setRespDTO(new CreateCustRespDTO(CustMapper.toDTO(saved)));
    }

    @Transactional(readOnly = true)
    public void get(GetCustCtx ctx) {
        String id = ctx.getReqDTO().getCustomerId();
        CustEntity entity = customerRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Customer not found: " + id));
        ctx.setRespDTO(new GetCustRespDTO(CustMapper.toDTO(entity)));
    }

    @Transactional(readOnly = true)
    public void list(ListCustsCtx ctx) {
        String status = ctx.getReqDTO() == null ? null : ctx.getReqDTO().getStatus();
        List<CustEntity> rows = (status == null || status.isBlank())
                ? customerRepository.findAll()
                : customerRepository.findByStatus(status);
        List<CustDTO> dtos = rows.stream().map(CustMapper::toDTO).toList();
        ctx.setRespDTO(new ListCustsRespDTO(dtos, dtos.size()));
    }

    @Transactional
    public void update(UpdateCustCtx ctx) {
        String id = ctx.getReqDTO().getCustomerId();
        CustDTO in = ctx.getReqDTO().getCustomer();
        CustEntity entity = customerRepository.findById(id)
                .orElseThrow(() -> new ResourceNotFoundException("Customer not found: " + id));

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

        CustEntity saved = customerRepository.save(entity);
        log.info("Updated customer {}", saved.getCustomerId());
        ctx.setRespDTO(new UpdateCustRespDTO(CustMapper.toDTO(saved)));
    }

    @Transactional
    public void delete(DeleteCustCtx ctx) {
        String id = ctx.getReqDTO().getCustomerId();
        if (!customerRepository.existsById(id)) {
            throw new ResourceNotFoundException("Customer not found: " + id);
        }
        customerRepository.deleteById(id);
        log.info("Deleted customer {}", id);
        ctx.setRespDTO(new DeleteCustRespDTO(id, true));
    }
}
