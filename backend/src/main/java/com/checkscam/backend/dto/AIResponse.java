package com.checkscam.backend.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class AIResponse {
    private String reply; // câu trả lời AI
    private boolean hasLookup; // có tra cứu dữ liệu hay không
    private String lookupType; // PHONE / BANK / URL
    private String lookupValue;
    private Integer reportCount;
    private String riskLevel; // SAFE / MEDIUM / HIGH
}
