package com.checkscam.backend.dto;

import lombok.Data;

@Data
public class AccountCreateDTO {
    private String email;
    private String name;
    private String password;
    private Integer roleId;
}
