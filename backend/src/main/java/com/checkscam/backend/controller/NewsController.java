package com.checkscam.backend.controller;

import com.checkscam.backend.dto.*;
import com.checkscam.backend.service.NewsService;
import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

@RestController
@RequestMapping("/api/news")
@RequiredArgsConstructor
public class NewsController {

    private final NewsService newsService;

    // ===================== PUBLIC =====================

    @GetMapping
    public ResponseEntity<Page<NewsListDTO>> getAllNews(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) Integer categoryId,
            @RequestParam(required = false) String keyword) {

        return ResponseEntity.ok(
                newsService.getNewsPage(page, size, categoryId, keyword));
    }

    @GetMapping("/latest")
    public ResponseEntity<List<NewsListDTO>> getLatest(
            @RequestParam(defaultValue = "5") int limit) {

        return ResponseEntity.ok(newsService.getLatest(limit));
    }

    @GetMapping("/{id}")
    public ResponseEntity<NewsResponseDTO> getNewsDetail(@PathVariable Integer id) {
        return ResponseEntity.ok(newsService.getById(id));
    }

    // ===================== ADMIN (PENDING) =====================

    @GetMapping("/pending")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<List<NewsListDTO>> getPendingNews() {
        return ResponseEntity.ok(newsService.getPending());
    }

    // ===================== ADMIN + CTV =====================

    @PostMapping
    @PreAuthorize("hasAnyRole('ADMIN','CTV')")
    public ResponseEntity<NewsResponseDTO> createNews(
            @RequestBody NewsCreateDTO dto) {

        return ResponseEntity.ok(newsService.create(dto));
    }

    @PostMapping("/with-file")
    @PreAuthorize("hasAnyRole('ADMIN','CTV')")
    public ResponseEntity<NewsResponseDTO> createNewsWithFile(
            @RequestParam String title,
            @RequestParam String content,
            @RequestParam String description,
            @RequestParam(required = false) Integer categoryId,
            @RequestParam(required = false) MultipartFile thumbnailFile) {

        return ResponseEntity.ok(
                newsService.createWithFile(
                        title, content, description, categoryId, thumbnailFile));
    }

    @PutMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMIN','CTV')")
    public ResponseEntity<NewsResponseDTO> updateNews(
            @PathVariable Integer id,
            @RequestBody NewsUpdateDTO dto) {

        return ResponseEntity.ok(newsService.update(id, dto));
    }

    @PutMapping("/{id}/with-file")
    @PreAuthorize("hasAnyRole('ADMIN','CTV')")
    public ResponseEntity<NewsResponseDTO> updateNewsWithFile(
            @PathVariable Integer id,
            @RequestParam String title,
            @RequestParam String content,
            @RequestParam String description,
            @RequestParam(required = false) Integer categoryId,
            @RequestParam(required = false) MultipartFile thumbnailFile) {

        return ResponseEntity.ok(
                newsService.updateWithFile(
                        id, title, content, description, categoryId, thumbnailFile));
    }

    // ===================== ADMIN ONLY =====================

    @PutMapping("/{id}/approve")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<NewsResponseDTO> approveNews(@PathVariable Integer id) {
        return ResponseEntity.ok(newsService.approve(id));
    }

    @PutMapping("/{id}/reject")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<NewsResponseDTO> rejectNews(
            @PathVariable Integer id,
            @RequestParam(required = false) String reason) {

        return ResponseEntity.ok(newsService.reject(id, reason));
    }

    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> deleteNews(@PathVariable Integer id) {
        newsService.delete(id);
        return ResponseEntity.ok("Deleted");
    }
}
