package com.checkscam.backend.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class ReportStatsDTO {

    private long totalReports;

    // theo loại
    private long phoneReports;
    private long bankReports;
    private long urlReports;

    // theo trạng thái
    private long pendingReports;
    private long approvedReports;
    private long rejectedReports;

    // theo risk level
    private long safeReports;
    private long mediumReports;
    private long highReports;
}
