package com.checkscam.backend.dto;

import lombok.Data;

@Data
public class NewsUpdateDTO {
    private String title;
    private String description;
    private String content;
    private String thumbnailUrl;
    private Integer categoryId;
}
