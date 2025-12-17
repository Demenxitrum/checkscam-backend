package com.checkscam.backend.repository;

import com.checkscam.backend.entity.LogActionTargetType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface LogActionTargetTypeRepository extends JpaRepository<LogActionTargetType, Integer> {

    Optional<LogActionTargetType> findByName(String name);
}
