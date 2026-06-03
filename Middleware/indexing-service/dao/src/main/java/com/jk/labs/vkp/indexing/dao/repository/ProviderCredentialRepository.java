package com.jk.labs.vkp.indexing.dao.repository;

import com.jk.labs.vkp.indexing.dao.entity.ProviderCredentialEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface ProviderCredentialRepository extends JpaRepository<ProviderCredentialEntity, String> {

    List<ProviderCredentialEntity> findByProviderType(String providerType);
}
