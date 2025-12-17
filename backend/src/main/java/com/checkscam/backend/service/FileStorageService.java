package com.checkscam.backend.service;

import org.springframework.web.multipart.MultipartFile;

public interface FileStorageService {

    String saveReportFile(Integer reportId, MultipartFile file);

    void createFolderIfNotExists(String path);
}
