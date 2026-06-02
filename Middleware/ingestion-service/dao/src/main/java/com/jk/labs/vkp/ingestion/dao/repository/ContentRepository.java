package com.jk.labs.vkp.ingestion.dao.repository;

import com.jk.labs.vkp.ingestion.dao.entity.ContentEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ContentRepository extends JpaRepository<ContentEntity, String> {

    List<ContentEntity> findByCompanyId(String companyId);
}
