package com.jk.labs.vkp.indexing.dao.repository;

import com.jk.labs.vkp.indexing.dao.entity.IndexingWorkflowEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface IndexingWorkflowRepository extends JpaRepository<IndexingWorkflowEntity, String> {
}
