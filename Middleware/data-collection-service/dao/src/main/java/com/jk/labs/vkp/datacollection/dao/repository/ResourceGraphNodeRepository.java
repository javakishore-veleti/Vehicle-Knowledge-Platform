package com.jk.labs.vkp.datacollection.dao.repository;

import com.jk.labs.vkp.datacollection.dao.entity.ResourceGraphNodeEntity;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ResourceGraphNodeRepository extends JpaRepository<ResourceGraphNodeEntity, String> {

    List<ResourceGraphNodeEntity> findByCompanyId(String companyId);

    List<ResourceGraphNodeEntity> findByCompanyIdAndResourceType(String companyId, String resourceType);

    /** Server-side paging for large graphs (100k+ rows). */
    Page<ResourceGraphNodeEntity> findByCompanyId(String companyId, Pageable pageable);

    long countByCompanyId(String companyId);
}
