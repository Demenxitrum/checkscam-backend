package com.checkscam.backend.dto;

import lombok.Data;

@Data
public class NewsCreateDTO {
    private String title;
    private String description;
    private String content;
    private String thumbnailUrl; // FE gửi link ảnh hoặc tên file
    private Integer categoryId; // có thể null nếu không phân loại
}
