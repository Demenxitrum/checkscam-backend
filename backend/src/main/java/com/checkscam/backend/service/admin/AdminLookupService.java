package com.checkscam.backend.service.admin;

import com.checkscam.backend.dto.admin.AdminLookupResponse;
import com.checkscam.backend.entity.LookupCache;
import com.checkscam.backend.entity.Report;
import com.checkscam.backend.repository.LookupCacheRepository;
import com.checkscam.backend.repository.ReportRepository;
import com.checkscam.backend.service.risk.RiskEngineExplainService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;

@Service
@RequiredArgsConstructor
public class AdminLookupService {

    private final LookupCacheRepository lookupCacheRepository;
    private final ReportRepository reportRepository;
    private final RiskEngineExplainService riskEngineExplainService;

    /**
     * ADMIN tra cứu chi tiết thực thể (PHONE / BANK / URL)
     * READ-ONLY – KHÔNG ảnh hưởng API khác
     */
    public AdminLookupResponse lookup(String type, String value) {

        if (type == null || value == null) {
            return null;
        }

        String entityType = type.trim().toUpperCase();
        String entityValue = value.trim();

        // =====================================================
        // 1. Lookup CORE DATA từ lookup_cache
        // =====================================================
        Optional<LookupCache> cacheOpt = lookupCacheRepository.findByValueAndType_Name(entityValue, entityType);

        if (cacheOpt.isEmpty()) {

            AdminLookupResponse empty = new AdminLookupResponse();

            empty.setEntityType(entityType);
            empty.setEntityValue(entityValue);
            empty.setNormalizedValue(entityValue);

        // ---------- Kết quả đánh giá ----------
            empty.setRiskScore(0);
            empty.setRiskLevel("UNKNOWN");
            empty.setConfidence(0.0);

        // ---------- Dữ liệu cộng đồng ----------
            empty.setReportCount(0);
            empty.setApprovedReports(0);
            empty.setPendingReports(0);
            empty.setRejectedReports(0);

        // ---------- Thời gian ----------
            empty.setFirstReportedAt(null);
            empty.setLastReportedAt(null);

        // ---------- Risk Engine ----------
            empty.setRiskSignals(Collections.emptyList());
            empty.setSignalWeights(Collections.emptyMap());

        // ---------- Source summary ----------
        Map<String, Boolean> sourceSummary = new LinkedHashMap<>();
            sourceSummary.put("community", false);
            sourceSummary.put("government", false);
            sourceSummary.put("news", false);
            sourceSummary.put("externalBlacklist", false);
            empty.setSourceSummary(sourceSummary);

        // ---------- Admin hints ----------
            empty.setAdminHints(
            List.of("Chưa có dữ liệu trong hệ thống")
        );
            empty.setLastUpdated(null);
            return empty;
        }


        LookupCache cache = cacheOpt.get();

        // =====================================================
        // 2. REPORT theo trạng thái (ADMIN dùng DB realtime)
        // =====================================================
        List<Report> approvedReports = reportRepository.findApprovedByValueAndType(entityValue, entityType);

        int approved = approvedReports.size();

        int pending = reportRepository.countByStatusAndValue(
                "PENDING", entityType, entityValue);

        int rejected = reportRepository.countByStatusAndValue(
                "REJECTED", entityType, entityValue);

        int totalReports = approved + pending + rejected;

        // =====================================================
        // 3. Giải thích Risk Engine (DẤU ẤN CÁ NHÂN)
        // =====================================================
        RiskEngineExplainService.ExplainResult explain = riskEngineExplainService.explain(cache, approvedReports);

        // =====================================================
        // 4. Build RESPONSE cho ADMIN
        // =====================================================
        AdminLookupResponse response = new AdminLookupResponse();

        // ---------- Thông tin cơ bản ----------
        response.setEntityType(entityType);
        response.setEntityValue(entityValue);
        response.setNormalizedValue(entityValue); // có thể normalize sau

        // ---------- Kết quả đánh giá ----------
        response.setRiskScore(explain.getRiskScore());
        response.setRiskLevel(explain.getRiskLevel());

        // =====================================================
        // CONFIDENCE – fallback logic (KHÔNG PHỤ THUỘC AI)
        // =====================================================
        Double confidence;

        if (approved >= 3) {
            confidence = 0.85;
        } else if (approved == 2) {
            confidence = 0.70;
        } else if (approved == 1) {
            confidence = 0.55;
        } else if (pending > 0) {
            confidence = 0.40;
        } else {
            confidence = 0.20;
        }

        response.setConfidence(confidence);

        // ---------- Dữ liệu cộng đồng ----------
        response.setReportCount(totalReports);
        response.setApprovedReports(approved);
        response.setPendingReports(pending);
        response.setRejectedReports(rejected);

        // =====================================================
        // 6. Thời gian REPORT
        // =====================================================
        LocalDateTime firstReportedAt = reportRepository.findFirstReportTime(entityType, entityValue);

        LocalDateTime lastReportedAt = reportRepository.findLastReportTime(entityType, entityValue);

        response.setFirstReportedAt(firstReportedAt);
        response.setLastReportedAt(lastReportedAt);

        // =====================================================
        // 7. Risk Signals + trọng số
        // =====================================================
        response.setRiskSignals(explain.getTriggeredRules());
        response.setSignalWeights(explain.getRuleWeights());

        // =====================================================
        // 8. Source summary
        // =====================================================
        Map<String, Boolean> sourceSummary = new LinkedHashMap<>();
        sourceSummary.put("community", totalReports > 0);
        sourceSummary.put("government", false);
        sourceSummary.put("news", false);
        sourceSummary.put("externalBlacklist", false);

        response.setSourceSummary(sourceSummary);

        // =====================================================
        // 9. Gợi ý cho ADMIN (ĂN ĐIỂM ĐỒ ÁN)
        // =====================================================
        List<String> adminHints = new ArrayList<>();

        if (approved == 0 && pending > 0) {
            adminHints.add("Có báo cáo đang chờ duyệt");
        }

        if (explain.getRiskScore() >= 70) {
            adminHints.add("Mức rủi ro cao – cần xem xét cảnh báo");
        }

        if (approved >= 3) {
            adminHints.add("Nhiều báo cáo đã duyệt – độ tin cậy cao");
        }

        response.setAdminHints(adminHints);

        // ---------- Metadata ----------
        response.setLastUpdated(cache.getUpdatedAt());

        return response;
    }
}
