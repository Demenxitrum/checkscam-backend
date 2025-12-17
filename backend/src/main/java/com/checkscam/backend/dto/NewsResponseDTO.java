package com.checkscam.backend.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class NewsResponseDTO {

    private Integer id;

    private String title;
    private String description;
    private String content;

    private String thumbnailUrl;

    private Integer categoryId;
    private String categoryName;

    private String createdAt; // format string cho dễ hiển thị
}
