package com.checkscam.backend.repository;

import com.checkscam.backend.entity.LogAction;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.JpaSpecificationExecutor;
import org.springframework.stereotype.Repository;

@Repository
public interface LogActionRepository
        extends JpaRepository<LogAction, Integer>, JpaSpecificationExecutor<LogAction> {
}
