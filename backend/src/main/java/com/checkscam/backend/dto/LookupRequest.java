package com.checkscam.backend.dto;

import lombok.Data;

@Data
public class LookupRequest {
    private String type; // PHONE, BANK, URL
    private String value;
}
