package com.checkscam.backend.dto;

import lombok.Data;

@Data
public class AccountUpdateDTO {
    private String name;
    private Integer roleId;
    private Integer statusId;
}
