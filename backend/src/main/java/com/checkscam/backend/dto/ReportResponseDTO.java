package com.checkscam.backend.dto;

import lombok.Data;
import java.util.List;

@Data
public class ReportResponseDTO {

    private Integer id;
    private String infoValue;
    private String description;
    private String userEmail;
    private String createdAt;

    private Integer typeId;
    private String typeName;

    private Integer statusId;
    private String statusName;

    private Integer riskLevelId;
    private String riskLevelName;

    private List<ReportEvidenceDTO> evidences;
}
