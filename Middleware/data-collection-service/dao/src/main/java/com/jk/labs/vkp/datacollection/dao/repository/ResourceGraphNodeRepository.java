package com.jk.labs.vkp.datacollection.dao.repository;

import com.jk.labs.vkp.datacollection.dao.entity.ResourceGraphNodeEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ResourceGraphNodeRepository extends JpaRepository<ResourceGraphNodeEntity, String> {

    List<ResourceGraphNodeEntity> findByCompanyId(String companyId);
}
