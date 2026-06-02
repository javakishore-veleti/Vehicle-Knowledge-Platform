package com.jk.labs.vkp.company.dao.repository;

import com.jk.labs.vkp.company.dao.entity.CompResourceEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface CompResourceRepository extends JpaRepository<CompResourceEntity, String> {

    List<CompResourceEntity> findByCompanyId(String companyId);

    Optional<CompResourceEntity> findByCompanyResourceIdAndCompanyId(String companyResourceId,
                                                                           String companyId);
}
