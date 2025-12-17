package com.checkscam.backend.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class AccountStatsDTO {

    private long totalAccounts;

    private long admins;
    private long ctvs;
    private long users;

    private long active;
    private long locked;
}
