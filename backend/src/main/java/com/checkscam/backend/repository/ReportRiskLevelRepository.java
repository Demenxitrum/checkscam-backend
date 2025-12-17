package com.checkscam.backend.repository;

import com.checkscam.backend.entity.ReportRiskLevel;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

@Repository
public interface ReportRiskLevelRepository extends JpaRepository<ReportRiskLevel, Integer> {
}
