package com.checkscam.backend.service.impl;

import com.checkscam.backend.dto.LookupRequest;
import com.checkscam.backend.dto.LookupResponse;
import com.checkscam.backend.entity.LookupCache;
import com.checkscam.backend.entity.LookupCacheType;
import com.checkscam.backend.repository.LookupCacheRepository;
import com.checkscam.backend.repository.LookupCacheTypeRepository;
import com.checkscam.backend.repository.ReportRepository;
import com.checkscam.backend.repository.ReportRiskLevelRepository;
import com.checkscam.backend.repository.ReportTypeRepository;
import com.checkscam.backend.service.LookupService;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;

@Service
@RequiredArgsConstructor
public class LookupServiceImpl implements LookupService {

    private final LookupCacheRepository cacheRepo;
    private final LookupCacheTypeRepository cacheTypeRepo;
    private final ReportRepository reportRepo;
    private final ReportTypeRepository typeRepo;
    private final ReportRiskLevelRepository riskRepo;

    // ===================================
    // VALIDATION
    // ===================================
    private void validatePhone(String phone) {
        if (phone == null || !phone.matches("^[0-9]{8,12}$")) {
            throw new RuntimeException("Phone sai định dạng");
        }
    }

    private void validateBank(String bank) {
        if (bank == null || !bank.matches("^[0-9]{8,16}$")) {
            throw new RuntimeException("Bank sai định dạng");
        }
    }

    private void validateURL(String url) {
        if (url == null || !(url.startsWith("http://") || url.startsWith("https://"))) {
            throw new RuntimeException("URL không có http/https");
        }
    }

    // ===================================
    // RISK LEVEL LOGIC
    // ===================================
    private int determineRisk(int count) {
        if (count == 0)
            return 1; // SAFE
        if (count <= 2)
            return 2; // MEDIUM
        return 3; // HIGH
    }

    private LookupResponse buildResponse(LookupCache cache) {
        return LookupResponse.builder()
                .type(cache.getType().getName())
                .value(cache.getValue())
                .reportCount(cache.getReportCount())
                .riskLevel(cache.getRiskLevel().getName())
                .exists(cache.getReportCount() > 0)
                .updatedAt(cache.getUpdatedAt().toString())
                .build();
    }

    private LookupCache buildAndSaveCache(LookupCacheType type, String value, int count) {

        int riskLevelId = determineRisk(count);

        var riskLevel = riskRepo.findById(riskLevelId)
                .orElseThrow(() -> new RuntimeException("Risk level not found: " + riskLevelId));

        LookupCache newCache = LookupCache.builder()
                .type(type)
                .value(value)
                .reportCount(count)
                .riskLevel(riskLevel)
                .updatedAt(LocalDateTime.now())
                .build();

        return cacheRepo.save(newCache);
    }

    // ===================================
    // LOOKUP PHONE
    // ===================================
    @Override
    public LookupResponse lookupPhone(String value) {

        validatePhone(value);

        LookupCacheType phoneType = cacheTypeRepo.findByName("PHONE")
                .orElseThrow(() -> new RuntimeException("Lookup type PHONE missing"));

        LookupCache cached = cacheRepo.findByTypeAndValue(phoneType, value);
        if (cached != null)
            return buildResponse(cached);

        var type = typeRepo.findByName("PHONE").orElseThrow();
        int count = reportRepo.countByTypeAndInfoValue(type, value);

        LookupCache newCache = buildAndSaveCache(phoneType, value, count);
        return buildResponse(newCache);
    }

    // ===================================
    // LOOKUP BANK
    // ===================================
    @Override
    public LookupResponse lookupBank(String value) {

        validateBank(value);

        LookupCacheType bankType = cacheTypeRepo.findByName("BANK")
                .orElseThrow(() -> new RuntimeException("Lookup type BANK missing"));

        LookupCache cached = cacheRepo.findByTypeAndValue(bankType, value);
        if (cached != null)
            return buildResponse(cached);

        var type = typeRepo.findByName("BANK").orElseThrow();
        int count = reportRepo.countByTypeAndInfoValue(type, value);

        LookupCache newCache = buildAndSaveCache(bankType, value, count);
        return buildResponse(newCache);
    }

    // ===================================
    // LOOKUP URL
    // ===================================
    @Override
    public LookupResponse lookupURL(String value) {

        validateURL(value);

        LookupCacheType urlType = cacheTypeRepo.findByName("URL")
                .orElseThrow(() -> new RuntimeException("Lookup type URL missing"));

        LookupCache cached = cacheRepo.findByTypeAndValue(urlType, value);
        if (cached != null)
            return buildResponse(cached);

        var type = typeRepo.findByName("URL").orElseThrow();
        int count = reportRepo.countByTypeAndInfoValue(type, value);

        LookupCache newCache = buildAndSaveCache(urlType, value, count);
        return buildResponse(newCache);
    }

    // ===================================
    // LOOKUP GENERIC
    // ===================================
    @Override
    public LookupResponse lookupGeneric(LookupRequest req) {

        return switch (req.getType().toUpperCase()) {
            case "PHONE" -> lookupPhone(req.getValue());
            case "BANK" -> lookupBank(req.getValue());
            case "URL" -> lookupURL(req.getValue());
            default -> throw new RuntimeException("Loại lookup không hợp lệ");
        };
    }
}
