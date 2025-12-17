package com.checkscam.backend.dto;

import lombok.Data;

@Data
public class LogActionDTO {
    private Integer id;
    private String action;

    private Integer accountId;
    private String accountEmail;

    private String targetType; // REPORT / ACCOUNT / NEWS...
    private Integer targetId;

    private String createdAt;
}
