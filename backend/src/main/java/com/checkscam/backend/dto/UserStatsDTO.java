package com.checkscam.backend.dto;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class UserStatsDTO {

    private long totalUsers;

    private long adminCount;
    private long ctvCount;
    private long normalUserCount;

    private long activeUsers;
    private long lockedUsers;
}
