package com.checkscam.backend.service.impl;

import com.checkscam.backend.service.FileStorageService;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.*;

@Service
public class FileStorageServiceImpl implements FileStorageService {

    @Value("${file.upload-dir}")
    private String uploadDir;

    @Override
    public String saveReportFile(Integer reportId, MultipartFile file) {

        try {
            // uploads/report/{reportId}
            Path reportDir = Paths.get(uploadDir, "report", reportId.toString());
            createFolderIfNotExists(reportDir.toString());

            String fileName = System.currentTimeMillis() + "_" +
                    file.getOriginalFilename().replaceAll("\\s+", "_");

            Path filePath = reportDir.resolve(fileName);

            Files.copy(
                    file.getInputStream(),
                    filePath,
                    StandardCopyOption.REPLACE_EXISTING);

            // Path public cho FE
            return "/uploads/report/" + reportId + "/" + fileName;

        } catch (IOException e) {
            throw new RuntimeException("Không thể lưu file upload", e);
        }
    }

    @Override
    public void createFolderIfNotExists(String path) {
        try {
            Files.createDirectories(Paths.get(path));
        } catch (IOException e) {
            throw new RuntimeException("Không thể tạo thư mục upload", e);
        }
    }
}
