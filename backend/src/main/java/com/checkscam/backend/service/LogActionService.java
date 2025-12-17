package com.checkscam.backend.service;

import com.checkscam.backend.dto.LogActionDTO;
import com.checkscam.backend.dto.LogActionFilterRequest;
import com.checkscam.backend.dto.LogActionListDTO;

public interface LogActionService {

    // ghi log (đang dùng trong các module khác)
    void log(Integer accountId, String action, String targetType, Integer targetId);

    // hỗ trợ lấy accountId từ email (đang dùng)
    Integer getAccountIdByEmail(String email);

    // API admin
    LogActionListDTO getLogs(int page, int size);

    LogActionListDTO filterLogs(LogActionFilterRequest filter, int page, int size);

    LogActionDTO getLog(Integer id);
}
