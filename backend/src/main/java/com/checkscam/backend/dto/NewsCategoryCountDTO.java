package com.checkscam.backend.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class NewsCategoryCountDTO {
    private String categoryName;
    private long count;
}
