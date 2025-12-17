package com.checkscam.backend.dto;

import lombok.Data;

import java.util.List;

@Data
public class LogActionListDTO {
    private List<LogActionDTO> items;
    private long totalItems;
    private int totalPages;
    private int page;
}
