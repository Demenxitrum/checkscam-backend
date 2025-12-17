package com.checkscam.backend.service.impl;

import com.checkscam.backend.service.FileStorageService;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

@Service
public class FileStorageServiceImpl implements FileStorageService {

    @Override
    public String saveReportFile(Integer reportId, MultipartFile file) {

        try {
            // Lấy thư mục gốc của project (tuyệt đối, không phụ thuộc target/)
            String projectDir = System.getProperty("user.dir");

            // uploads/report/{reportId}/
            String uploadDir = projectDir + "/uploads/report/" + reportId + "/";

            // Tạo thư mục nếu chưa có
            createFolderIfNotExists(uploadDir);

            // Tên file mới: thời gian + tên gốc (replace space)
            String fileName = System.currentTimeMillis() + "_" +
                    file.getOriginalFilename().replace(" ", "_");

            Path filePath = Paths.get(uploadDir + fileName);

            // Lưu file
            Files.copy(file.getInputStream(), filePath);

            // Trả về path relative để lưu DB
            return "uploads/report/" + reportId + "/" + fileName;

        } catch (IOException e) {
            throw new RuntimeException("Không thể lưu file: " + e.getMessage());
        }
    }

    @Override
    public void createFolderIfNotExists(String path) {
        File folder = new File(path);
        if (!folder.exists()) {
            folder.mkdirs();
        }
    }
}
