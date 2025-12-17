package com.checkscam.backend.service;

import com.checkscam.backend.dto.DashboardOverviewDTO;
import com.checkscam.backend.dto.DailyReportDTO;
import com.checkscam.backend.dto.TopReportValueDTO;

import java.util.List;

public interface DashboardService {

    DashboardOverviewDTO getSummary();

    List<DailyReportDTO> getDailyReport();

    List<TopReportValueDTO> getTopReportValues();
}
