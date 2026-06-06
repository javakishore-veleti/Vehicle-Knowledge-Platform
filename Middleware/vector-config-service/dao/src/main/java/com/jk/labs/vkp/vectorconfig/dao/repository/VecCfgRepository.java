package com.jk.labs.vkp.vectorconfig.dao.repository;

import com.jk.labs.vkp.vectorconfig.dao.entity.VecCfgEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface VecCfgRepository extends JpaRepository<VecCfgEntity, String> {

    List<VecCfgEntity> findByCompanyResourceId(String companyResourceId);

    List<VecCfgEntity> findByCompanyId(String companyId);

    List<VecCfgEntity> findByStatus(String status);

    List<VecCfgEntity> findByCompanyResourceIdAndIsPrimaryTrue(String companyResourceId);
}
