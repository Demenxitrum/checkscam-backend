package com.checkscam.backend.controller;

import com.checkscam.backend.dto.LookupRequest;
import com.checkscam.backend.dto.LookupResponse;
import com.checkscam.backend.service.LookupService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/lookup")
@RequiredArgsConstructor
public class LookupController {

    private final LookupService lookupService;

    // =====================================================
    // ✅ USER LOOKUP – UNIFIED (KHUYẾN NGHỊ CHO FE)
    // GET /api/lookup?type=PHONE&value=0886...
    // =====================================================
    @GetMapping
    public ResponseEntity<LookupResponse> lookupUnified(
            @RequestParam String type,
            @RequestParam String value) {
        return ResponseEntity.ok(
                lookupService.lookupByType(type, value));
    }

    // =====================================================
    // ✅ USER LOOKUP – BACKWARD COMPATIBLE (KHÔNG XOÁ)
    // =====================================================

    // GET /api/lookup/phone?value=0886...
    @GetMapping("/phone")
    public ResponseEntity<LookupResponse> lookupPhone(@RequestParam String value) {
        return ResponseEntity.ok(lookupService.lookupPhone(value));
    }

    // GET /api/lookup/bank?value=123456789
    @GetMapping("/bank")
    public ResponseEntity<LookupResponse> lookupBank(@RequestParam String value) {
        return ResponseEntity.ok(lookupService.lookupBank(value));
    }

    // GET /api/lookup/url?value=example.com
    @GetMapping("/url")
    public ResponseEntity<LookupResponse> lookupURL(@RequestParam String value) {
        return ResponseEntity.ok(lookupService.lookupURL(value));
    }

    // =====================================================
    // ⚠️ POST LOOKUP – GIỮ LẠI NẾU FE/CLIENT CŨ DÙNG
    // POST /api/lookup
    // =====================================================
    @PostMapping
    public ResponseEntity<LookupResponse> lookupGeneric(
            @RequestBody LookupRequest req) {
        return ResponseEntity.ok(
                lookupService.lookupGeneric(req));
    }
}
