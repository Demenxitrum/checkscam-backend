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

    @GetMapping("/phone")
    public ResponseEntity<LookupResponse> lookupPhone(@RequestParam String value) {
        return ResponseEntity.ok(lookupService.lookupPhone(value));
    }

    @GetMapping("/bank")
    public ResponseEntity<LookupResponse> lookupBank(@RequestParam String value) {
        return ResponseEntity.ok(lookupService.lookupBank(value));
    }

    @GetMapping("/url")
    public ResponseEntity<LookupResponse> lookupURL(@RequestParam String value) {
        return ResponseEntity.ok(lookupService.lookupURL(value));
    }

    @PostMapping
    public ResponseEntity<LookupResponse> lookupGeneric(@RequestBody LookupRequest req) {
        return ResponseEntity.ok(lookupService.lookupGeneric(req));
    }
}
