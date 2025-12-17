package com.checkscam.backend.dto;

import lombok.Data;
import java.util.List;

@Data
public class ReportListDTO {
    private List<ReportResponseDTO> items;
    private long totalItems;
    private int totalPages;
    private int page;
}
