package com.checkscam.backend.dto;

import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Data;
import lombok.NoArgsConstructor;

@Data
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TopReportValueDTO {

    private String value; // SĐT / STK / URL
    private String typeName; // PHONE / BANK / URL
    private long total; // số lần bị báo cáo
}
