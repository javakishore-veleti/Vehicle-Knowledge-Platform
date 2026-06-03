package com.jk.labs.vkp.indexing.dao.repository;

import com.jk.labs.vkp.indexing.dao.entity.ResourceGraphIndexLogEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ResourceGraphIndexLogRepository extends JpaRepository<ResourceGraphIndexLogEntity, String> {

    List<ResourceGraphIndexLogEntity> findByCompanyIdOrderByCreatedDtDesc(String companyId);

    /** Dedup: existing run for the same (company, workflow, formula) in the given states. */
    List<ResourceGraphIndexLogEntity> findByCompanyIdAndWfIdAndIndexFormulaIdAndStatusIn(
            String companyId, String wfId, String indexFormulaId, List<String> statuses);
}
