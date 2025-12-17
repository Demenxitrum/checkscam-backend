package com.checkscam.backend.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class LookupResponse {

    private String type;
    private String value;
    private int reportCount;
    private String riskLevel;
    private boolean exists;
    private String updatedAt;
}
