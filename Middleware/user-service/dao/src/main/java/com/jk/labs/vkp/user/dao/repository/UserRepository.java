package com.jk.labs.vkp.user.dao.repository;

import com.jk.labs.vkp.user.dao.entity.UserEntity;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface UserRepository extends JpaRepository<UserEntity, String> {

    Optional<UserEntity> findByEmail(String email);

    Optional<UserEntity> findByResetToken(String resetToken);

    boolean existsByEmail(String email);
}
