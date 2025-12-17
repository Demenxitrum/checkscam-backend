package com.checkscam.backend.service.impl;

import com.checkscam.backend.dto.*;
import com.checkscam.backend.entity.*;
import com.checkscam.backend.repository.*;
import com.checkscam.backend.service.LogActionService;
import com.checkscam.backend.specification.LogActionSpecifications;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.*;
import org.springframework.data.jpa.domain.Specification;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;

@Service
@RequiredArgsConstructor
public class LogActionServiceImpl implements LogActionService {

    private final LogActionRepository logRepo;
    private final LogActionTargetTypeRepository targetTypeRepo;
    private final AccountRepository accountRepo;

    private static final DateTimeFormatter F = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    // ================== LOG (dùng bởi các module khác) ==================
    @Override
    public void log(Integer accountId, String action, String targetType, Integer targetId) {

        Account acc = null;
        if (accountId != null) {
            acc = accountRepo.findById(accountId).orElse(null);
        }

        LogActionTargetType type = targetTypeRepo.findByName(targetType)
                .orElseThrow(() -> new RuntimeException("TargetType not found: " + targetType));

        LogAction log = LogAction.builder()
                .account(acc)
                .action(action)
                .targetType(type)
                .targetId(targetId)
                .createdAt(LocalDateTime.now())
                .build();

        logRepo.save(log);
    }

    @Override
    public Integer getAccountIdByEmail(String email) {
        return accountRepo.findByEmail(email)
                .map(Account::getId)
                .orElse(null);
    }

    // ================== ADMIN API ==================

    @Override
    public LogActionListDTO getLogs(int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        Page<LogAction> p = logRepo.findAll(pageable);
        return mapPageToListDTO(p, page);
    }

    @Override
    public LogActionListDTO filterLogs(LogActionFilterRequest filter, int page, int size) {
        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());
        Specification<LogAction> spec = LogActionSpecifications.build(filter);
        Page<LogAction> p = logRepo.findAll(spec, pageable);
        return mapPageToListDTO(p, page);
    }

    @Override
    public LogActionDTO getLog(Integer id) {
        LogAction log = logRepo.findById(id)
                .orElseThrow(() -> new RuntimeException("Log not found: " + id));
        return toDTO(log);
    }

    // ================== MAPPING ==================

    private LogActionListDTO mapPageToListDTO(Page<LogAction> page, int pageIndex) {
        LogActionListDTO dto = new LogActionListDTO();
        dto.setItems(page.getContent().stream().map(this::toDTO).toList());
        dto.setTotalItems(page.getTotalElements());
        dto.setTotalPages(page.getTotalPages());
        dto.setPage(pageIndex);
        return dto;
    }

    private LogActionDTO toDTO(LogAction log) {
        LogActionDTO dto = new LogActionDTO();
        dto.setId(log.getId());
        dto.setAction(log.getAction());

        if (log.getAccount() != null) {
            dto.setAccountId(log.getAccount().getId());
            dto.setAccountEmail(log.getAccount().getEmail());
        }

        if (log.getTargetType() != null) {
            dto.setTargetType(log.getTargetType().getName());
        }

        dto.setTargetId(log.getTargetId());

        dto.setCreatedAt(
                log.getCreatedAt() != null ? log.getCreatedAt().format(F) : null);

        return dto;
    }
}
