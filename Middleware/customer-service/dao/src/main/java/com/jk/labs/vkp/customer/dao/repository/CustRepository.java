package com.jk.labs.vkp.customer.dao.repository;

import com.jk.labs.vkp.customer.dao.entity.CustEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface CustRepository extends JpaRepository<CustEntity, String> {

    List<CustEntity> findByStatus(String status);
}
