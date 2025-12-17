package com.checkscam.backend.dto;

import lombok.Data;
import lombok.Builder;

@Data
@Builder
public class AccountDetailDTO {
    private Integer id;
    private String email;
    private String name;
    private String role;
    private String status;
    private String createdAt;
}
