package com.checkscam.backend.service.impl;

import com.checkscam.backend.service.FileUploadService;
import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.*;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;

@Service
@RequiredArgsConstructor
public class FileUploadServiceImpl implements FileUploadService {

    private static final String ROOT_UPLOAD = "uploads/";

    @Override
    public String saveFile(MultipartFile file) {

        if (file == null || file.isEmpty()) {
            throw new RuntimeException("File is empty");
        }

        try {
            // Folder theo ngày
            String dateFolder = LocalDate.now()
                    .format(DateTimeFormatter.ofPattern("yyyy/MM/dd"));

            Path uploadPath = Paths.get(ROOT_UPLOAD + dateFolder);

            if (!Files.exists(uploadPath)) {
                Files.createDirectories(uploadPath);
            }

            // Tên file mới
            String originalName = file.getOriginalFilename();
            String fileName = System.currentTimeMillis() + "_" + originalName;

            Path filePath = uploadPath.resolve(fileName);

            Files.copy(file.getInputStream(), filePath, StandardCopyOption.REPLACE_EXISTING);

            return "/uploads/" + dateFolder + "/" + fileName;

        } catch (IOException e) {
            throw new RuntimeException("Cannot save file: " + e.getMessage(), e);
        }
    }

    @Override
    public boolean deleteFile(String filePath) {

        try {
            String cleanPath = filePath.replace("/uploads/", "");
            Path fullPath = Paths.get(ROOT_UPLOAD + cleanPath);

            if (Files.exists(fullPath)) {
                Files.delete(fullPath);
                return true;
            }

            return false;

        } catch (Exception e) {
            return false;
        }
    }
}
