package com.jk.labs.vkp.cef.admin.repository;

import com.jk.labs.vkp.cef.admin.entity.CefStrategyEntity;
import org.springframework.data.jpa.repository.JpaRepository;

public interface CefStrategyRepository extends JpaRepository<CefStrategyEntity, String> {
    boolean existsByName(String name);
}
