package com.checkscam.backend.mapper;

import com.checkscam.backend.dto.ReportEvidenceDTO;
import com.checkscam.backend.dto.ReportResponseDTO;
import com.checkscam.backend.entity.Report;
import com.checkscam.backend.entity.ReportEvidence;

import java.util.stream.Collectors;

public class ReportMapper {

    public static ReportResponseDTO toDTO(Report r) {
        ReportResponseDTO dto = new ReportResponseDTO();

        dto.setId(r.getId());
        dto.setInfoValue(r.getInfoValue());
        dto.setDescription(r.getDescription());
        dto.setUserEmail(r.getUserEmail());
        dto.setCreatedAt(r.getCreatedAt().toString());

        dto.setTypeId(r.getType().getId());
        dto.setTypeName(r.getType().getName());

        dto.setStatusId(r.getStatus().getId());
        dto.setStatusName(r.getStatus().getName());

        dto.setRiskLevelId(r.getRiskLevel().getId());
        dto.setRiskLevelName(r.getRiskLevel().getName());

        // ===============================
        // 🔥 BỔ SUNG: MAP EVIDENCES
        // ===============================
        if (r.getEvidences() != null) {
            dto.setEvidences(
                    r.getEvidences().stream()
                            .map(ReportMapper::toEvidenceDTO)
                            .collect(Collectors.toList()));
        }

        return dto;
    }

    private static ReportEvidenceDTO toEvidenceDTO(ReportEvidence e) {
        ReportEvidenceDTO dto = new ReportEvidenceDTO();
        dto.setId(e.getId());
        dto.setFilePath(e.getFilePath());
        return dto;
    }
}
