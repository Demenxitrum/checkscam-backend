package com.checkscam.backend.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class DashboardSummaryDTO {

    private ReportStatsDTO reportStats;
    private UserStatsDTO userStats;
    private NewsStatsDTO newsStats;
    private LookupStatsDTO lookupStats;
}
