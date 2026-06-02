package com.jk.labs.vkp.customer.dao.repository;

import com.jk.labs.vkp.customer.dao.entity.CustResourceEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;
import java.util.Optional;

@Repository
public interface CustResourceRepository extends JpaRepository<CustResourceEntity, String> {

    List<CustResourceEntity> findByCustomerId(String customerId);

    Optional<CustResourceEntity> findByCustomerResourceIdAndCustomerId(String customerResourceId,
                                                                           String customerId);
}
