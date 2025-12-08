package com.checkscam.backend.service;

import com.checkscam.backend.dto.NewsCreateDTO;
import com.checkscam.backend.dto.NewsListDTO;
import com.checkscam.backend.dto.NewsResponseDTO;
import com.checkscam.backend.dto.NewsUpdateDTO;
import org.springframework.data.domain.Page;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

public interface NewsService {

    // Lấy danh sách tin (phân trang + filter + search)
    Page<NewsListDTO> getNewsPage(int page, int size, Integer categoryId, String keyword);

    // Lấy chi tiết 1 tin
    NewsResponseDTO getById(Integer id);

    // Lấy N bài mới nhất (dùng cho trang chủ)
    List<NewsListDTO> getLatest(int limit);

    // Tạo tin (ADMIN + CTV)
    NewsResponseDTO create(NewsCreateDTO dto);

    // Cập nhật tin (ADMIN + CTV)
    NewsResponseDTO update(Integer id, NewsUpdateDTO dto);

    // Thêm mới – tạo tin kèm file thumbnail
    NewsResponseDTO createWithFile(String title,
            String content,
            String description,
            Integer categoryId,
            MultipartFile thumbnailFile);

    // Thêm mới – cập nhật tin kèm file thumbnail
    NewsResponseDTO updateWithFile(Integer id,
            String title,
            String content,
            String description,
            Integer categoryId,
            MultipartFile thumbnailFile);

    // Xoá tin (ADMIN)
    void delete(Integer id);
}
