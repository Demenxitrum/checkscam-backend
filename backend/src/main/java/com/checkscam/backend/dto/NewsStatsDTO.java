package com.checkscam.backend.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class NewsStatsDTO {

    private long totalNews;
    private long totalCategories;
}
