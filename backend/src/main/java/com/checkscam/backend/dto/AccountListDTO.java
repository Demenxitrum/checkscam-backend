package com.checkscam.backend.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class AccountListDTO {
    private Integer id;
    private String email;
    private String name;
    private String role;
    private String status;
}
