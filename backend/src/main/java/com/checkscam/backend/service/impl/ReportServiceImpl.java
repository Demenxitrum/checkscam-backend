package com.checkscam.backend.service.impl;

import com.checkscam.backend.dto.*;
import com.checkscam.backend.entity.*;
import com.checkscam.backend.mapper.ReportMapper;
import com.checkscam.backend.repository.*;
import com.checkscam.backend.service.FileStorageService;
import com.checkscam.backend.service.LogActionService;
import com.checkscam.backend.service.ReportService;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.*;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class ReportServiceImpl implements ReportService {

    private final ReportRepository reportRepo;
    private final ReportTypeRepository typeRepo;
    private final ReportStatusRepository statusRepo;
    private final ReportRiskLevelRepository riskRepo;
    private final ReportEvidenceRepository evidenceRepo;
    private final LogActionService logService;
    private final FileStorageService fileStorageService;

    private String getCurrentUserEmail() {
        try {
            Object principal = SecurityContextHolder.getContext()
                    .getAuthentication().getPrincipal();

            if (principal instanceof org.springframework.security.core.userdetails.User user) {
                return user.getUsername();
            }
        } catch (Exception ignored) {
        }
        return null;
    }

    private Integer getCurrentUserId() {
        try {
            Object p = SecurityContextHolder.getContext()
                    .getAuthentication().getPrincipal();

            if (p instanceof org.springframework.security.core.userdetails.User user) {
                return logService.getAccountIdByEmail(user.getUsername());
            }
        } catch (Exception ignored) {
        }
        return null;
    }

    // ============================================================
    // CREATE REPORT
    // ============================================================
    @Override
    public ReportResponseDTO create(ReportCreateRequest req, MultipartFile[] files) {

        ReportType type = typeRepo.findByName(req.getType().toUpperCase())
                .orElseThrow(() -> new RuntimeException("Report type not found: " + req.getType()));

        ReportStatus pending = statusRepo.findById(1)
                .orElseThrow(() -> new RuntimeException("PENDING status missing"));

        ReportRiskLevel safe = riskRepo.findById(1)
                .orElseThrow(() -> new RuntimeException("SAFE risk missing"));

        Report report = new Report();
        report.setInfoValue(req.getInfoValue());
        report.setDescription(req.getDescription());
        report.setUserEmail(getCurrentUserEmail());
        report.setType(type);
        report.setStatus(pending);
        report.setRiskLevel(safe);
        report.setCreatedAt(LocalDateTime.now());

        Report saved = reportRepo.save(report);

        // =============================
        // SAVE FILE EVIDENCES (REAL FILE UPLOAD)
        // =============================
        if (files != null) {
            for (MultipartFile f : files) {
                if (!f.isEmpty()) {

                    // 1) Lưu file thật vào server
                    String fileUrl = fileStorageService.saveReportFile(saved.getId(), f);

                    // 2) Lưu filePath (URL public) vào DB
                    evidenceRepo.save(
                            ReportEvidence.builder()
                                    .report(saved)
                                    .filePath(fileUrl)
                                    .build());
                }
            }
        }

        logService.log(getCurrentUserId(), "CREATE_REPORT", "REPORT", saved.getId());
        saved.setEvidences(evidenceRepo.findByReport(saved));
        return ReportMapper.toDTO(saved);
    }

    // ============================================================
    // GET REPORT LIST (PAGINATION)
    // ============================================================
    @Override
    public ReportListDTO getAll(int page, int size) {

        Pageable pageable = PageRequest.of(
                page,
                size,
                Sort.by("createdAt").descending());

        Page<Report> p = reportRepo.findAll(pageable);

        ReportListDTO dto = new ReportListDTO();
        dto.setItems(p.getContent().stream().map(ReportMapper::toDTO).toList());
        dto.setTotalItems(p.getTotalElements());
        dto.setTotalPages(p.getTotalPages());
        dto.setPage(page);

        return dto;
    }

    // ============================================================
    // GET DETAIL
    // ============================================================
    @Override
    public ReportResponseDTO getDetail(Integer id) {
        return ReportMapper.toDTO(
                reportRepo.findById(id)
                        .orElseThrow(() -> new RuntimeException("Report not found")));
    }

    // ============================================================
    // APPROVE
    // ============================================================
    @Override
    public ReportResponseDTO approve(Integer id) {
        Report r = reportRepo.findById(id)
                .orElseThrow(() -> new RuntimeException("Report not found"));

        r.setStatus(statusRepo.findById(2).orElseThrow());
        reportRepo.save(r);

        logService.log(getCurrentUserId(), "APPROVE_REPORT", "REPORT", id);

        return ReportMapper.toDTO(r);
    }

    // ============================================================
    // REJECT
    // ============================================================
    @Override
    public ReportResponseDTO reject(Integer id) {
        Report r = reportRepo.findById(id)
                .orElseThrow(() -> new RuntimeException("Report not found"));

        r.setStatus(statusRepo.findById(3).orElseThrow());
        reportRepo.save(r);

        logService.log(getCurrentUserId(), "REJECT_REPORT", "REPORT", id);

        return ReportMapper.toDTO(r);
    }

    // ============================================================
    // UPDATE DESCRIPTION
    // ============================================================
    @Override
    public ReportResponseDTO update(Integer id, ReportUpdateRequest req) {
        Report r = reportRepo.findById(id)
                .orElseThrow(() -> new RuntimeException("Report not found"));

        r.setDescription(req.getDescription());
        reportRepo.save(r);

        logService.log(getCurrentUserId(), "UPDATE_REPORT", "REPORT", id);

        return ReportMapper.toDTO(r);
    }

    // ============================================================
    // DELETE
    // ============================================================
    @Override
    public void delete(Integer id) {
        reportRepo.deleteById(id);
        logService.log(getCurrentUserId(), "DELETE_REPORT", "REPORT", id);
    }
}
