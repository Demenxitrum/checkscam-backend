package com.checkscam.backend.controller.admin;

import com.checkscam.backend.dto.admin.AdminLookupResponse;
import com.checkscam.backend.service.admin.AdminLookupService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/admin/lookup")
@RequiredArgsConstructor
public class AdminLookupController {

    private final AdminLookupService adminLookupService;

    /**
     * ADMIN tra cứu chi tiết thực thể (PHONE / BANK / URL)
     *
     * Ví dụ:
     * GET /api/admin/lookup?type=PHONE&value=0974079626
     */
    @GetMapping
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<AdminLookupResponse> lookup(
            @RequestParam String type,
            @RequestParam String value) {
        AdminLookupResponse response = adminLookupService.lookup(type, value);

        if (response == null) {
            return ResponseEntity.notFound().build();
        }

        return ResponseEntity.ok(response);
    }
}
