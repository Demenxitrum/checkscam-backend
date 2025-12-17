package com.checkscam.backend.controller;

import com.checkscam.backend.dto.DashboardOverviewDTO;
import com.checkscam.backend.dto.DailyReportDTO;
import com.checkscam.backend.dto.TopReportValueDTO;
import com.checkscam.backend.service.DashboardService;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api/dashboard")
@RequiredArgsConstructor
public class DashboardController {

    private final DashboardService dashboardService;

    // Tổng quan (sử dụng DashboardOverviewDTO)
    @GetMapping("/summary")
    public ResponseEntity<DashboardOverviewDTO> summary() {
        return ResponseEntity.ok(dashboardService.getSummary());
    }

    // Biểu đồ theo ngày
    @GetMapping("/daily")
    public ResponseEntity<List<DailyReportDTO>> dailyReports() {
        return ResponseEntity.ok(dashboardService.getDailyReport());
    }

    // Top value bị báo cáo nhiều nhất
    @GetMapping("/top-values")
    public ResponseEntity<List<TopReportValueDTO>> topValues() {
        return ResponseEntity.ok(dashboardService.getTopReportValues());
    }
}
