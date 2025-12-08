package com.checkscam.backend.service;

import org.springframework.web.multipart.MultipartFile;

public interface FileUploadService {

    // Lưu 1 file & trả về đường dẫn tương đối (/uploads/yyyy/MM/dd/file.png)
    String saveFile(MultipartFile file);

    // Xóa file
    boolean deleteFile(String filePath);
}
