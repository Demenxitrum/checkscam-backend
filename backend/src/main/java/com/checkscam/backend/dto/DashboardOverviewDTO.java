package com.checkscam.backend.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

import java.util.List;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class DashboardOverviewDTO {

    // Tổng quan
    private long totalReports;
    private long totalAccounts;
    private long totalNews;

    // Theo trạng thái
    private long pendingReports;
    private long approvedReports;
    private long rejectedReports;

    // Biểu đồ
    private List<DailyReportDTO> last7Days;

    // Thống kê theo loại report
    private List<ReportTypeStatDTO> byType;

    // Top value bị báo cáo nhiều nhất
    private List<TopReportValueDTO> topReportValues;
}
