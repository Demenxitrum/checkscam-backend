package com.checkscam.backend.service.impl;

import com.checkscam.backend.dto.NewsCreateDTO;
import com.checkscam.backend.dto.NewsListDTO;
import com.checkscam.backend.dto.NewsResponseDTO;
import com.checkscam.backend.dto.NewsUpdateDTO;
import com.checkscam.backend.entity.News;
import com.checkscam.backend.entity.NewsCategory;
import com.checkscam.backend.repository.NewsCategoryRepository;
import com.checkscam.backend.repository.NewsRepository;
import com.checkscam.backend.service.FileUploadService;
import com.checkscam.backend.service.LogActionService;
import com.checkscam.backend.service.NewsService;

import lombok.RequiredArgsConstructor;
import org.springframework.data.domain.*;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.time.format.DateTimeFormatter;
import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
public class NewsServiceImpl implements NewsService {

    private final NewsRepository newsRepo;
    private final NewsCategoryRepository categoryRepo;
    private final LogActionService logService;
    private final FileUploadService fileUploadService; // 👈 thêm

    private Integer getCurrentUserId() {
        try {
            Object principal = SecurityContextHolder.getContext()
                    .getAuthentication()
                    .getPrincipal();

            if (principal instanceof org.springframework.security.core.userdetails.User user) {
                String email = user.getUsername();
                return logService.getAccountIdByEmail(email);
            }
        } catch (Exception ignored) {
        }
        return null;
    }

    private static final DateTimeFormatter DATE_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    // =====================================================
    // PUBLIC METHODS
    // =====================================================

    @Override
    public Page<NewsListDTO> getNewsPage(int page, int size, Integer categoryId, String keyword) {
        if (page < 0)
            page = 0;
        if (size <= 0)
            size = 10;

        Pageable pageable = PageRequest.of(page, size, Sort.by("createdAt").descending());

        Page<News> newsPage;

        boolean hasCategory = (categoryId != null);
        boolean hasKeyword = (keyword != null && !keyword.trim().isEmpty());

        if (hasCategory && hasKeyword) {
            newsPage = newsRepo.findByCategory_IdAndTitleContainingIgnoreCase(
                    categoryId, keyword.trim(), pageable);
        } else if (hasCategory) {
            newsPage = newsRepo.findByCategory_Id(categoryId, pageable);
        } else if (hasKeyword) {
            newsPage = newsRepo.findByTitleContainingIgnoreCase(keyword.trim(), pageable);
        } else {
            newsPage = newsRepo.findAll(pageable);
        }

        List<NewsListDTO> content = newsPage.getContent()
                .stream()
                .map(this::toListDTO)
                .collect(Collectors.toList());

        return new PageImpl<>(content, pageable, newsPage.getTotalElements());
    }

    @Override
    public NewsResponseDTO getById(Integer id) {
        News news = newsRepo.findById(id)
                .orElseThrow(() -> new RuntimeException("News not found: " + id));
        return toResponseDTO(news);
    }

    @Override
    public List<NewsListDTO> getLatest(int limit) {
        List<News> list = newsRepo.findTop5ByOrderByCreatedAtDesc();
        if (limit > 0 && limit < list.size()) {
            list = list.subList(0, limit);
        }
        return list.stream()
                .map(this::toListDTO)
                .collect(Collectors.toList());
    }

    // ========== CŨ: Tạo tin dùng JSON (không file) ==========
    @Override
    public NewsResponseDTO create(NewsCreateDTO dto) {

        NewsCategory category = null;
        if (dto.getCategoryId() != null) {
            category = categoryRepo.findById(dto.getCategoryId())
                    .orElseThrow(() -> new RuntimeException("NewsCategory not found: " + dto.getCategoryId()));
        }

        News news = News.builder()
                .title(dto.getTitle())
                .content(dto.getContent())
                .description(dto.getDescription())
                .thumbnail(dto.getThumbnailUrl())
                .thumbnailUrl(dto.getThumbnailUrl())
                .category(category)
                .build();

        News saved = newsRepo.save(news);

        logService.log(getCurrentUserId(), "CREATE_NEWS", "NEWS", saved.getId());

        return toResponseDTO(saved);
    }

    // ========== MỚI: Tạo tin kèm file thumbnail ==========
    @Override
    public NewsResponseDTO createWithFile(String title,
            String content,
            String description,
            Integer categoryId,
            MultipartFile thumbnailFile) {

        NewsCategory category = null;
        if (categoryId != null) {
            category = categoryRepo.findById(categoryId)
                    .orElseThrow(() -> new RuntimeException("NewsCategory not found: " + categoryId));
        }

        String thumbnailUrl = null;
        if (thumbnailFile != null && !thumbnailFile.isEmpty()) {
            thumbnailUrl = fileUploadService.saveFile(thumbnailFile);
        }

        News news = News.builder()
                .title(title)
                .content(content)
                .description(description)
                .thumbnail(thumbnailUrl)
                .thumbnailUrl(thumbnailUrl)
                .category(category)
                .build();

        News saved = newsRepo.save(news);
        logService.log(getCurrentUserId(), "CREATE_NEWS", "NEWS", saved.getId());
        return toResponseDTO(saved);
    }

    // ========== CŨ: Update tin dùng JSON ==========
    @Override
    public NewsResponseDTO update(Integer id, NewsUpdateDTO dto) {

        News news = newsRepo.findById(id)
                .orElseThrow(() -> new RuntimeException("News not found: " + id));

        news.setTitle(dto.getTitle());
        news.setContent(dto.getContent());
        news.setDescription(dto.getDescription());
        news.setThumbnail(dto.getThumbnailUrl());
        news.setThumbnailUrl(dto.getThumbnailUrl());

        if (dto.getCategoryId() != null) {
            NewsCategory category = categoryRepo.findById(dto.getCategoryId())
                    .orElseThrow(() -> new RuntimeException("NewsCategory not found: " + dto.getCategoryId()));
            news.setCategory(category);
        } else {
            news.setCategory(null);
        }

        News saved = newsRepo.save(news);

        logService.log(getCurrentUserId(), "UPDATE_NEWS", "NEWS", id);

        return toResponseDTO(saved);
    }

    // ========== MỚI: Update tin kèm file thumbnail ==========
    @Override
    public NewsResponseDTO updateWithFile(Integer id,
            String title,
            String content,
            String description,
            Integer categoryId,
            MultipartFile thumbnailFile) {

        News news = newsRepo.findById(id)
                .orElseThrow(() -> new RuntimeException("News not found: " + id));

        news.setTitle(title);
        news.setContent(content);
        news.setDescription(description);

        if (categoryId != null) {
            NewsCategory category = categoryRepo.findById(categoryId)
                    .orElseThrow(() -> new RuntimeException("NewsCategory not found: " + categoryId));
            news.setCategory(category);
        } else {
            news.setCategory(null);
        }

        if (thumbnailFile != null && !thumbnailFile.isEmpty()) {
            String thumbnailUrl = fileUploadService.saveFile(thumbnailFile);
            news.setThumbnail(thumbnailUrl);
            news.setThumbnailUrl(thumbnailUrl);
        }

        News saved = newsRepo.save(news);
        logService.log(getCurrentUserId(), "UPDATE_NEWS", "NEWS", id);
        return toResponseDTO(saved);
    }

    @Override
    public void delete(Integer id) {
        News news = newsRepo.findById(id)
                .orElseThrow(() -> new RuntimeException("News not found: " + id));

        newsRepo.delete(news);

        logService.log(getCurrentUserId(), "DELETE_NEWS", "NEWS", id);
    }

    // =====================================================
    // MAPPING HELPER
    // =====================================================

    private NewsResponseDTO toResponseDTO(News n) {
        return NewsResponseDTO.builder()
                .id(n.getId())
                .title(n.getTitle())
                .description(n.getDescription())
                .content(n.getContent())
                .thumbnailUrl(n.getThumbnailUrl())
                .categoryId(n.getCategory() != null ? n.getCategory().getId() : null)
                .categoryName(n.getCategory() != null ? n.getCategory().getName() : null)
                .createdAt(n.getCreatedAt() != null ? n.getCreatedAt().format(DATE_FORMAT) : null)
                .build();
    }

    private NewsListDTO toListDTO(News n) {
        return NewsListDTO.builder()
                .id(n.getId())
                .title(n.getTitle())
                .thumbnailUrl(n.getThumbnailUrl())
                .categoryName(n.getCategory() != null ? n.getCategory().getName() : null)
                .createdAt(n.getCreatedAt() != null ? n.getCreatedAt().format(DATE_FORMAT) : null)
                .build();
    }
}
