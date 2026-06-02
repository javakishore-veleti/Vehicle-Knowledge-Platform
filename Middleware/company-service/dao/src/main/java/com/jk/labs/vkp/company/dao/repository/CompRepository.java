package com.jk.labs.vkp.company.dao.repository;

import com.jk.labs.vkp.company.dao.entity.CompEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CompRepository extends JpaRepository<CompEntity, String> {

    List<CompEntity> findByStatus(String status);
}
