package com.checkscam.backend.service;

import com.checkscam.backend.dto.*;
import org.springframework.data.domain.Page;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;

public interface NewsService {

        Page<NewsListDTO> getNewsPage(int page, int size, Integer categoryId, String keyword);

        NewsResponseDTO getById(Integer id);

        List<NewsListDTO> getLatest(int limit);

        // ADMIN + CTV
        NewsResponseDTO create(NewsCreateDTO dto);

        NewsResponseDTO update(Integer id, NewsUpdateDTO dto);

        NewsResponseDTO createWithFile(
                        String title,
                        String content,
                        String description,
                        Integer categoryId,
                        MultipartFile thumbnailFile);

        NewsResponseDTO updateWithFile(
                        Integer id,
                        String title,
                        String content,
                        String description,
                        Integer categoryId,
                        MultipartFile thumbnailFile);

        // ADMIN ONLY
        NewsResponseDTO approve(Integer id);

        NewsResponseDTO reject(Integer id, String reason);

        void delete(Integer id);

        // ADMIN: danh sách tin chờ duyệt
        List<NewsListDTO> getPending();
}
