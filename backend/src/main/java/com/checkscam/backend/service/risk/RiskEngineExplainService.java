package com.checkscam.backend.service.risk;

import com.checkscam.backend.entity.LookupCache;
import com.checkscam.backend.entity.Report;
import lombok.Data;
import org.springframework.stereotype.Service;

import java.util.*;

/**
 * Giải thích kết quả Risk Engine cho ADMIN
 * ❌ Không chấm điểm lại
 * ❌ Không thay đổi dữ liệu
 * ✅ Chỉ giải thích vì sao hệ thống đánh giá như vậy
 */
@Service
public class RiskEngineExplainService {

    public ExplainResult explain(
            LookupCache cache,
            List<Report> approvedReports) {

        ExplainResult result = new ExplainResult();

        // ============================
        // 1. Risk score (ước lượng từ level)
        // ============================
        int riskScore = mapRiskLevelToScore(
                cache.getRiskLevel().getName());
        result.setRiskScore(riskScore);
        result.setRiskLevel(cache.getRiskLevel().getName());

        // ============================
        // 2. Rules triggered + weights
        // ============================
        List<String> rules = new ArrayList<>();
        Map<String, Integer> ruleWeights = new LinkedHashMap<>();

        // Rule 1: Bị report nhiều lần
        if (cache.getReportCount() >= 3) {
            rules.add("MULTI_REPORT");
            ruleWeights.put("MULTI_REPORT", 10);
        }

        // Rule 2: Có report đã được duyệt
        if (!approvedReports.isEmpty()) {
            rules.add("COMMUNITY_CONFIRMED");
            ruleWeights.put("COMMUNITY_CONFIRMED", 20);
        }

        // Rule 3: Risk level cao từ hệ thống
        if ("HIGH".equals(cache.getRiskLevel().getName())) {
            rules.add("HIGH_RISK_LEVEL");
            ruleWeights.put("HIGH_RISK_LEVEL", 30);
        }

        result.setTriggeredRules(rules);
        result.setRuleWeights(ruleWeights);

        return result;
    }

    // ============================
    // PRIVATE HELPERS
    // ============================

    private int mapRiskLevelToScore(String riskLevel) {
        return switch (riskLevel) {
            case "HIGH" -> 85;
            case "MEDIUM" -> 55;
            default -> 20;
        };
    }

    // ============================
    // INNER DTO (CHỈ DÙNG NỘI BỘ)
    // ============================

    @Data
    public static class ExplainResult {
        private int riskScore;
        private String riskLevel;

        // Explainable signals
        private List<String> triggeredRules;

        // NEW — rule → trọng số
        private Map<String, Integer> ruleWeights;
    }
}
