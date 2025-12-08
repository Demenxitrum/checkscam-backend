package com.checkscam.backend.repository;

import com.checkscam.backend.entity.Account;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface AccountRepository extends JpaRepository<Account, Integer> {

    Optional<Account> findByEmail(String email);

    boolean existsByEmail(String email);

    // Dashboard: đếm theo role name
    long countByRole_Name(String name);

    // Dashboard: đếm theo status id (1=ACTIVE, 2=LOCKED/INACTIVE)
    long countByStatus_Id(Integer statusId);
}
