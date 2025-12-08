package com.checkscam.backend.controller;

import com.checkscam.backend.dto.NewsCreateDTO;
import com.checkscam.backend.dto.NewsListDTO;
import com.checkscam.backend.dto.NewsResponseDTO;
import com.checkscam.backend.dto.NewsUpdateDTO;
import com.checkscam.backend.service.NewsService;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.Page;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/news")
@RequiredArgsConstructor
public class NewsController {

    private final NewsService newsService;

    // PUBLIC: danh sách tin (có phân trang + filter + search)
    @GetMapping
    public ResponseEntity<Page<NewsListDTO>> getAllNews(
            @RequestParam(defaultValue = "0") int page,
            @RequestParam(defaultValue = "10") int size,
            @RequestParam(required = false) Integer categoryId,
            @RequestParam(required = false) String keyword) {
        return ResponseEntity.ok(
                newsService.getNewsPage(page, size, categoryId, keyword));
    }

    // PUBLIC: chi tiết tin
    @GetMapping("/{id}")
    public ResponseEntity<NewsResponseDTO> getNewsDetail(@PathVariable Integer id) {
        return ResponseEntity.ok(newsService.getById(id));
    }

    // PUBLIC: 5 tin mới nhất
    @GetMapping("/latest")
    public ResponseEntity<?> getLatest(
            @RequestParam(defaultValue = "5") int limit) {
        return ResponseEntity.ok(newsService.getLatest(limit));
    }

    // ADMIN + CTV: tạo tin (JSON – cũ, không file)
    @PostMapping
    @PreAuthorize("hasAnyRole('ADMIN','CTV')")
    public ResponseEntity<NewsResponseDTO> createNews(
            @RequestBody NewsCreateDTO dto) {
        return ResponseEntity.ok(newsService.create(dto));
    }

    // ADMIN + CTV: tạo tin kèm file thumbnail (MỚI)
    @PostMapping("/with-file")
    @PreAuthorize("hasAnyRole('ADMIN','CTV')")
    public ResponseEntity<NewsResponseDTO> createNewsWithFile(
            @RequestParam String title,
            @RequestParam String content,
            @RequestParam String description,
            @RequestParam(required = false) Integer categoryId,
            @RequestParam(required = false) MultipartFile thumbnailFile) {

        return ResponseEntity.ok(
                newsService.createWithFile(title, content, description, categoryId, thumbnailFile));
    }

    // ADMIN + CTV: sửa tin (JSON – cũ, không file)
    @PutMapping("/{id}")
    @PreAuthorize("hasAnyRole('ADMIN','CTV')")
    public ResponseEntity<NewsResponseDTO> updateNews(
            @PathVariable Integer id,
            @RequestBody NewsUpdateDTO dto) {
        return ResponseEntity.ok(newsService.update(id, dto));
    }

    // ADMIN + CTV: sửa tin kèm file thumbnail (MỚI)
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
                newsService.updateWithFile(id, title, content, description, categoryId, thumbnailFile));
    }

    // ADMIN: xóa tin
    @DeleteMapping("/{id}")
    @PreAuthorize("hasRole('ADMIN')")
    public ResponseEntity<?> deleteNews(@PathVariable Integer id) {
        newsService.delete(id);
        return ResponseEntity.ok("Deleted");
    }
}
