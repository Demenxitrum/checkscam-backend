package com.checkscam.backend.service.impl;

import com.checkscam.backend.dto.*;
import com.checkscam.backend.repository.AccountRepository;
import com.checkscam.backend.repository.NewsRepository;
import com.checkscam.backend.repository.ReportRepository;
import com.checkscam.backend.service.DashboardService;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;

import java.sql.Date;
import java.time.LocalDate;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class DashboardServiceImpl implements DashboardService {

        private final ReportRepository reportRepo;
        private final AccountRepository accountRepo;
        private final NewsRepository newsRepo;

        // =================================================
        // 1) Tổng quan dashboard
        // =================================================
        @Override
        public DashboardOverviewDTO getSummary() {

                long totalReports = reportRepo.count();
                long totalAccounts = accountRepo.count();
                long totalNews = newsRepo.count();

                long pendingReports = reportRepo.countByStatus_Id(1); // Pending
                long approvedReports = reportRepo.countByStatus_Id(2); // Approved
                long rejectedReports = reportRepo.countByStatus_Id(3); // Rejected

                // Biểu đồ 7 ngày gần nhất
                List<DailyReportDTO> last7Days = getDailyReport()
                                .stream()
                                .limit(7)
                                .collect(Collectors.toList());

                // Thống kê số report theo từng loại
                List<ReportTypeStatDTO> byType = reportRepo.countReportsByType()
                                .stream()
                                .map(row -> ReportTypeStatDTO.builder()
                                                .typeId((Integer) row[0])
                                                .typeName((String) row[1])
                                                .total(((Number) row[2]).longValue())
                                                .build())
                                .collect(Collectors.toList());

                // Top value bị báo cáo nhiều nhất
                List<TopReportValueDTO> topValues = getTopReportValues();

                return DashboardOverviewDTO.builder()
                                .totalReports(totalReports)
                                .totalAccounts(totalAccounts)
                                .totalNews(totalNews)

                                .pendingReports(pendingReports)
                                .approvedReports(approvedReports)
                                .rejectedReports(rejectedReports)

                                .last7Days(last7Days)
                                .byType(byType)
                                .topReportValues(topValues)

                                .build();
        }

        // =================================================
        // 2) Thống kê theo ngày
        // =================================================
        @Override
        public List<DailyReportDTO> getDailyReport() {

                return reportRepo.countReportsByDate()
                                .stream()
                                .map(row -> {
                                        Date date = (Date) row[0];
                                        long total = ((Number) row[1]).longValue();

                                        return DailyReportDTO.builder()
                                                        .date(date.toLocalDate().toString())
                                                        .total(total)
                                                        .build();
                                })
                                .collect(Collectors.toList());
        }

        // =================================================
        // 3) Top value bị báo cáo nhiều
        // =================================================
        @Override
        public List<TopReportValueDTO> getTopReportValues() {

                return reportRepo.findTopReportedValues(PageRequest.of(0, 10))
                                .stream()
                                .map(row -> TopReportValueDTO.builder()
                                                .value((String) row[0])
                                                .typeName((String) row[1])
                                                .total(((Number) row[2]).longValue())
                                                .build())
                                .collect(Collectors.toList());
        }
}
