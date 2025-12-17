package com.checkscam.backend.repository;

import com.checkscam.backend.entity.AccountRole;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface AccountRoleRepository extends JpaRepository<AccountRole, Integer> {

    Optional<AccountRole> findByName(String name);
}
