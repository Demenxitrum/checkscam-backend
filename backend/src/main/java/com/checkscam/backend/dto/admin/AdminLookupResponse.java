package com.checkscam.backend.dto.admin;

import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Data
public class AdminLookupResponse {

    // ========================
    // THÔNG TIN CƠ BẢN
    // ========================
    private String entityType;
    private String entityValue;
    private String normalizedValue; // +84..., clean URL...

    // ========================
    // KẾT QUẢ ĐÁNH GIÁ
    // ========================
    private Integer riskScore;
    private String riskLevel;
    private Double confidence;

    // ========================
    // DỮ LIỆU CỘNG ĐỒNG (CHI TIẾT)
    // ========================
    private Integer reportCount;
    private Integer approvedReports;
    private Integer pendingReports;
    private Integer rejectedReports;
    private LocalDateTime firstReportedAt;
    private LocalDateTime lastReportedAt;

    // ========================
    // DẤU ẤN CÁ NHÂN – GIẢI THÍCH
    // ========================
    private List<String> riskSignals;
    private Map<String, Integer> signalWeights;

    // ========================
    // NGUỒN DỮ LIỆU
    // ========================
    private Map<String, Boolean> sourceSummary;
    // community / gov / news / blacklist

    // ========================
    // GỢI Ý CHO ADMIN
    // ========================
    private List<String> adminHints;

    // ========================
    // METADATA
    // ========================
    private LocalDateTime lastUpdated;
}
