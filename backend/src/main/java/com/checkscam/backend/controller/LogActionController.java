package com.checkscam.backend.controller;

import com.checkscam.backend.dto.LogActionDTO;
import com.checkscam.backend.dto.LogActionFilterRequest;
import com.checkscam.backend.dto.LogActionListDTO;
import com.checkscam.backend.service.LogActionService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/logs")
@RequiredArgsConstructor
public class LogActionController {

    private final LogActionService logActionService;

    // Lấy danh sách log (phân trang)
    @GetMapping
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<LogActionListDTO> getLogs(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {

        return ResponseEntity.ok(logActionService.getLogs(page, size));
    }

    // Lọc log theo nhiều tiêu chí
    @PostMapping("/search")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<LogActionListDTO> filterLogs(
            @RequestBody LogActionFilterRequest filter,
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {

        return ResponseEntity.ok(logActionService.filterLogs(filter, page, size));
    }

    // Chi tiết 1 log
    @GetMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<LogActionDTO> getDetail(@PathVariable Integer id) {
        return ResponseEntity.ok(logActionService.getLog(id));
    }
}
