package com.checkscam.backend.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class SystemStatsDTO {

    private long totalLookupCached; // tổng số giá trị đã từng tra cứu (lookup_cache)
    private long highRiskReports; // số report có risk HIGH
}
