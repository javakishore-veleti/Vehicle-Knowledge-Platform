package com.jk.labs.vkp.customer.service;

import com.jk.labs.vkp.customer.common.dto.resource.CreateCustResourceCtx;
import com.jk.labs.vkp.customer.common.dto.resource.CreateCustResourceRespDTO;
import com.jk.labs.vkp.customer.common.dto.resource.CustResourceDTO;
import com.jk.labs.vkp.customer.common.dto.resource.DeleteCustResourceCtx;
import com.jk.labs.vkp.customer.common.dto.resource.DeleteCustResourceRespDTO;
import com.jk.labs.vkp.customer.common.dto.resource.ListCustResourcesCtx;
import com.jk.labs.vkp.customer.common.dto.resource.ListCustResourcesRespDTO;
import com.jk.labs.vkp.customer.common.dto.resource.UpdateCustResourceCtx;
import com.jk.labs.vkp.customer.common.dto.resource.UpdateCustResourceRespDTO;
import com.jk.labs.vkp.customer.common.enums.Status;
import com.jk.labs.vkp.customer.common.error.ResourceNotFoundException;
import com.jk.labs.vkp.customer.dao.entity.CustResourceEntity;
import com.jk.labs.vkp.customer.dao.repository.CustRepository;
import com.jk.labs.vkp.customer.dao.repository.CustResourceRepository;
import com.jk.labs.vkp.customer.service.mapper.CustResourceMapper;
import com.jk.labs.vkp.customer.utils.AuditUtils;
import com.jk.labs.vkp.customer.utils.IdGenerator;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.Instant;
import java.util.List;

/**
 * Business logic for customer resource CRUD (a related table of customer).
 *
 * Every method takes only its use case {@code Ctx}.
 */
@Service
@Slf4j
@RequiredArgsConstructor
public class CustResourceService {

    private final CustResourceRepository resourceRepository;
    private final CustRepository customerRepository;

    @Transactional
    public void create(CreateCustResourceCtx ctx) {
        String customerId = ctx.getReqDTO().getCustomerId();
        ensureCustomerExists(customerId);

        CustResourceDTO in = ctx.getReqDTO().getResource();
        Instant now = Instant.now();

        CustResourceEntity entity = CustResourceMapper.toEntity(in);
        entity.setCustomerResourceId(IdGenerator.newId());
        entity.setCustomerId(customerId);
        entity.setStatus(in.getStatus() != null ? in.getStatus() : Status.DEFAULT);
        entity.setCreatedDt(now);
        entity.setUpdatedDt(now);
        entity.setCreatedBy(AuditUtils.actorOrDefault(in.getCreatedBy()));
        entity.setUpdatedBy(entity.getCreatedBy());

        CustResourceEntity saved = resourceRepository.save(entity);
        log.info("Created customer resource {} for customer {}", saved.getCustomerResourceId(), customerId);
        ctx.setRespDTO(new CreateCustResourceRespDTO(CustResourceMapper.toDTO(saved)));
    }

    @Transactional(readOnly = true)
    public void list(ListCustResourcesCtx ctx) {
        String customerId = ctx.getReqDTO().getCustomerId();
        ensureCustomerExists(customerId);
        List<CustResourceEntity> rows = resourceRepository.findByCustomerId(customerId);
        List<CustResourceDTO> dtos = rows.stream().map(CustResourceMapper::toDTO).toList();
        ctx.setRespDTO(new ListCustResourcesRespDTO(dtos, dtos.size()));
    }

    @Transactional
    public void update(UpdateCustResourceCtx ctx) {
        String customerId = ctx.getReqDTO().getCustomerId();
        String resourceId = ctx.getReqDTO().getResourceId();
        CustResourceEntity entity = resourceRepository
                .findByCustomerResourceIdAndCustomerId(resourceId, customerId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Customer resource not found: " + resourceId + " for customer " + customerId));

        CustResourceDTO in = ctx.getReqDTO().getResource();
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

        CustResourceEntity saved = resourceRepository.save(entity);
        log.info("Updated customer resource {}", saved.getCustomerResourceId());
        ctx.setRespDTO(new UpdateCustResourceRespDTO(CustResourceMapper.toDTO(saved)));
    }

    @Transactional
    public void delete(DeleteCustResourceCtx ctx) {
        String customerId = ctx.getReqDTO().getCustomerId();
        String resourceId = ctx.getReqDTO().getResourceId();
        CustResourceEntity entity = resourceRepository
                .findByCustomerResourceIdAndCustomerId(resourceId, customerId)
                .orElseThrow(() -> new ResourceNotFoundException(
                        "Customer resource not found: " + resourceId + " for customer " + customerId));
        resourceRepository.delete(entity);
        log.info("Deleted customer resource {}", resourceId);
        ctx.setRespDTO(new DeleteCustResourceRespDTO(resourceId, true));
    }

    private void ensureCustomerExists(String customerId) {
        if (!customerRepository.existsById(customerId)) {
            throw new ResourceNotFoundException("Customer not found: " + customerId);
        }
    }
}
