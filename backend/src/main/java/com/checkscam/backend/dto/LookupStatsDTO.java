package com.checkscam.backend.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class LookupStatsDTO {

    // tổng số giá trị đã được lưu cache (số phone / stk / url từng bị tra cứu)
    private long totalLookupTargets;

    // số giá trị đã từng bị báo cáo (reportCount > 0)
    private long riskyTargets;
}
