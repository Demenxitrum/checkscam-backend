package com.checkscam.backend.repository;

import com.checkscam.backend.entity.ReportType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface ReportTypeRepository extends JpaRepository<ReportType, Integer> {
    Optional<ReportType> findByName(String name);
}
