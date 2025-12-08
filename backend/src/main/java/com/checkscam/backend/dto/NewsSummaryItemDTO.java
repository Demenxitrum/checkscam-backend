package com.checkscam.backend.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class NewsSummaryItemDTO {

    private Integer id;
    private String title;
    private String thumbnailUrl;
    private String categoryName;
    private String createdAt;
}
