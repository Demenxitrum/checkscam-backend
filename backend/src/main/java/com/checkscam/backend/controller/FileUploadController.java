package com.checkscam.backend.controller;

import com.checkscam.backend.service.FileUploadService;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.web.servlet.support.ServletUriComponentsBuilder;

import java.util.*;

@RestController
@RequestMapping("/api/upload")
@RequiredArgsConstructor
public class FileUploadController {

    private final FileUploadService fileUploadService;

    // =======================
    // UPLOAD 1 FILE
    // =======================
    @PostMapping("/file")
    public ResponseEntity<?> uploadFile(@RequestParam("files") MultipartFile file) {

        if (file == null || file.isEmpty()) {
            return ResponseEntity.badRequest().body(Map.of("error", "File is empty"));
        }

        // Validate type
        String type = file.getContentType();
        if (type == null ||
                !(type.equals("image/jpeg") ||
                        type.equals("image/png") ||
                        type.equals("application/pdf"))) {
            return ResponseEntity.badRequest().body(Map.of("error", "Invalid file type (jpg/png/pdf only)"));
        }

        // Validate max size (5MB)
        long max = 5 * 1024 * 1024;
        if (file.getSize() > max) {
            return ResponseEntity.badRequest().body(Map.of("error", "Max file size is 5MB"));
        }

        // Lưu file
        String relativeUrl = fileUploadService.saveFile(file);

        // Trả về URL đầy đủ cho frontend
        String fullUrl = ServletUriComponentsBuilder.fromCurrentContextPath()
                .path(relativeUrl)
                .toUriString();

        return ResponseEntity.ok(Map.of("fileUrl", fullUrl));
    }

    // =======================
    // UPLOAD MULTIPLE FILES
    // =======================
    @PostMapping("/multiple")
    public ResponseEntity<?> uploadMultiple(@RequestParam("files") MultipartFile[] files) {

        if (files == null || files.length == 0) {
            return ResponseEntity.badRequest().body(Map.of("error", "No files provided"));
        }

        List<String> urls = new ArrayList<>();

        for (MultipartFile f : files) {
            if (f.isEmpty())
                continue;

            String type = f.getContentType();
            if (type == null ||
                    !(type.equals("image/jpeg") ||
                            type.equals("image/png") ||
                            type.equals("application/pdf"))) {
                continue;
            }

            String url = fileUploadService.saveFile(f);

            String fullUrl = ServletUriComponentsBuilder.fromCurrentContextPath()
                    .path(url)
                    .toUriString();

            urls.add(fullUrl);
        }

        return ResponseEntity.ok(urls);
    }

    // =======================
    // DELETE FILE
    // =======================
    @DeleteMapping("/delete")
    public ResponseEntity<?> deleteFile(@RequestParam String filePath) {

        boolean deleted = fileUploadService.deleteFile(filePath);

        if (deleted) {
            return ResponseEntity.ok(Map.of("message", "File deleted"));
        } else {
            return ResponseEntity.badRequest().body(Map.of("error", "File not found or cannot delete"));
        }
    }
}
