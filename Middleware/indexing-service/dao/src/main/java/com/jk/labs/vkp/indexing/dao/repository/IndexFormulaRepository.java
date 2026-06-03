package com.jk.labs.vkp.indexing.dao.repository;

import com.jk.labs.vkp.indexing.dao.entity.IndexFormulaEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface IndexFormulaRepository extends JpaRepository<IndexFormulaEntity, String> {
}
