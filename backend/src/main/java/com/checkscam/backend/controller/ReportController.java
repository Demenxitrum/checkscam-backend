package com.checkscam.backend.controller;

import com.checkscam.backend.dto.*;
import com.checkscam.backend.service.ReportService;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/report")
@RequiredArgsConstructor
public class ReportController {

    private final ReportService reportService;

    @PostMapping
    public ResponseEntity<ReportResponseDTO> create(
            @ModelAttribute ReportCreateRequest req,
            @RequestParam(required = false) MultipartFile[] files) {

        return ResponseEntity.ok(reportService.create(req, files));
    }

    @GetMapping
    public ResponseEntity<ReportListDTO> getAll(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size) {

        return ResponseEntity.ok(reportService.getAll(page, size));
    }

    @GetMapping("/{id}")
    public ResponseEntity<ReportResponseDTO> detail(@PathVariable Integer id) {
        return ResponseEntity.ok(reportService.getDetail(id));
    }

    @PutMapping("/{id}/approve")
    public ResponseEntity<ReportResponseDTO> approve(@PathVariable Integer id) {
        return ResponseEntity.ok(reportService.approve(id));
    }

    @PutMapping("/{id}/reject")
    public ResponseEntity<ReportResponseDTO> reject(@PathVariable Integer id) {
        return ResponseEntity.ok(reportService.reject(id));
    }

    @PutMapping("/{id}")
    public ResponseEntity<ReportResponseDTO> update(
            @PathVariable Integer id,
            @RequestBody ReportUpdateRequest req) {

        return ResponseEntity.ok(reportService.update(id, req));
    }

    @DeleteMapping("/{id}")
    public ResponseEntity<?> delete(@PathVariable Integer id) {
        reportService.delete(id);
        return ResponseEntity.ok("Deleted");
    }
}
