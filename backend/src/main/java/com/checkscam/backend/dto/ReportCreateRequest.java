package com.checkscam.backend.dto;

import lombok.Data;

@Data
public class ReportCreateRequest {
    private String infoValue;
    private String type; // PHONE / BANK / URL
    private String description;
}
