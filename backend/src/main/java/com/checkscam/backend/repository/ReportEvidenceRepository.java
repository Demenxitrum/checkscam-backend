package com.checkscam.backend.repository;

import com.checkscam.backend.entity.Report;
import com.checkscam.backend.entity.ReportEvidence;
import org.springframework.data.jpa.repository.JpaRepository;
import java.util.List;

public interface ReportEvidenceRepository extends JpaRepository<ReportEvidence, Integer> {

    List<ReportEvidence> findByReport(Report report);
}
