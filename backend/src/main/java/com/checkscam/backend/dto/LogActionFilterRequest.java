package com.checkscam.backend.dto;

import lombok.Data;

import java.time.LocalDateTime;

@Data
public class LogActionFilterRequest {

    private Integer accountId; // lọc theo user
    private String action; // chứa chuỗi (LIKE)
    private String targetType; // REPORT / ACCOUNT / NEWS...

    private LocalDateTime from; // từ ngày (optional)
    private LocalDateTime to; // đến ngày (optional)
}
