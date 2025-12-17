package com.checkscam.backend.service.impl;

import com.checkscam.backend.dto.*;
import com.checkscam.backend.entity.News;
import com.checkscam.backend.entity.NewsCategory;
import com.checkscam.backend.entity.enums.NewsStatus;
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

import java.time.LocalDateTime;
import java.time.format.DateTimeFormatter;
import java.util.List;

@Service
@RequiredArgsConstructor
public class NewsServiceImpl implements NewsService {

    private final NewsRepository newsRepo;
    private final NewsCategoryRepository categoryRepo;
    private final LogActionService logService;
    private final FileUploadService fileUploadService;

    private static final DateTimeFormatter DATE_FORMAT = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");

    // ===================== HELPER =====================

    private Integer getCurrentUserId() {
        try {
            Object principal = SecurityContextHolder.getContext()
                    .getAuthentication().getPrincipal();
            if (principal instanceof org.springframework.security.core.userdetails.User user) {
                return logService.getAccountIdByEmail(user.getUsername());
            }
        } catch (Exception ignored) {
        }
        return null;
    }

    private boolean isAdmin() {
        return SecurityContextHolder.getContext()
                .getAuthentication()
                .getAuthorities()
                .stream()
                .anyMatch(a -> a.getAuthority().equals("ROLE_ADMIN"));
    }

    // ===================== PUBLIC =====================

    @Override
    public Page<NewsListDTO> getNewsPage(int page, int size,
            Integer categoryId, String keyword) {

        Pageable pageable = PageRequest.of(
                Math.max(page, 0),
                size <= 0 ? 10 : size,
                Sort.by("createdAt").descending());

        Page<News> pageData;

        if (categoryId != null && keyword != null && !keyword.isBlank()) {
            pageData = newsRepo.findByStatusAndCategory_IdAndTitleContainingIgnoreCase(
                    NewsStatus.PUBLISHED, categoryId, keyword.trim(), pageable);
        } else if (categoryId != null) {
            pageData = newsRepo.findByStatusAndCategory_Id(
                    NewsStatus.PUBLISHED, categoryId, pageable);
        } else if (keyword != null && !keyword.isBlank()) {
            pageData = newsRepo.findByStatusAndTitleContainingIgnoreCase(
                    NewsStatus.PUBLISHED, keyword.trim(), pageable);
        } else {
            pageData = newsRepo.findByStatus(
                    NewsStatus.PUBLISHED, pageable);
        }

        List<NewsListDTO> list = pageData.getContent()
                .stream()
                .map(this::toListDTO)
                .toList();

        return new PageImpl<>(list, pageable, pageData.getTotalElements());
    }

    @Override
    public NewsResponseDTO getById(Integer id) {
        News news = newsRepo.findById(id)
                .orElseThrow(() -> new RuntimeException("News not found"));

        if (news.getStatus() != NewsStatus.PUBLISHED && !isAdmin()) {
            throw new RuntimeException("Tin chưa được duyệt");
        }

        return toResponseDTO(news);
    }

    @Override
    public List<NewsListDTO> getLatest(int limit) {
        return newsRepo.findTop5ByStatusOrderByCreatedAtDesc(NewsStatus.PUBLISHED)
                .stream()
                .limit(limit)
                .map(this::toListDTO)
                .toList();
    }

    // ===================== CREATE =====================

    @Override
    public NewsResponseDTO create(NewsCreateDTO dto) {
        return saveNews(
                dto.getTitle(),
                dto.getContent(),
                dto.getDescription(),
                dto.getThumbnailUrl(),
                dto.getCategoryId(),
                null);
    }

    @Override
    public NewsResponseDTO createWithFile(String title, String content,
            String description, Integer categoryId,
            MultipartFile thumbnailFile) {

        String thumbnailUrl = null;
        if (thumbnailFile != null && !thumbnailFile.isEmpty()) {
            thumbnailUrl = fileUploadService.saveFile(thumbnailFile);
        }

        return saveNews(
                title,
                content,
                description,
                thumbnailUrl,
                categoryId,
                thumbnailUrl);
    }

    private NewsResponseDTO saveNews(String title, String content,
            String description, String thumbnailUrl,
            Integer categoryId, String thumb) {

        NewsCategory category = null;
        if (categoryId != null) {
            category = categoryRepo.findById(categoryId)
                    .orElseThrow(() -> new RuntimeException("Category not found"));
        }

        Integer userId = getCurrentUserId();
        boolean admin = isAdmin();

        News news = News.builder()
                .title(title)
                .content(content)
                .description(description)
                .thumbnail(thumb)
                .thumbnailUrl(thumbnailUrl)
                .category(category)
                .createdBy(userId)
                .status(admin ? NewsStatus.PUBLISHED : NewsStatus.PENDING)
                .approvedBy(admin ? userId : null)
                .approvedAt(admin ? LocalDateTime.now() : null)
                .build();

        News saved = newsRepo.save(news);
        logService.log(userId, "CREATE_NEWS", "NEWS", saved.getId());

        return toResponseDTO(saved);
    }

    // ===================== UPDATE =====================

    @Override
    public NewsResponseDTO update(Integer id, NewsUpdateDTO dto) {
        News news = getEditableNews(id);

        news.setTitle(dto.getTitle());
        news.setContent(dto.getContent());
        news.setDescription(dto.getDescription());
        news.setThumbnailUrl(dto.getThumbnailUrl());

        if (dto.getCategoryId() != null) {
            news.setCategory(categoryRepo.findById(dto.getCategoryId())
                    .orElseThrow(() -> new RuntimeException("Category not found")));
        } else {
            news.setCategory(null);
        }

        logService.log(getCurrentUserId(), "UPDATE_NEWS", "NEWS", id);
        return toResponseDTO(newsRepo.save(news));
    }

    @Override
    public NewsResponseDTO updateWithFile(Integer id, String title,
            String content, String description,
            Integer categoryId, MultipartFile file) {

        News news = getEditableNews(id);

        news.setTitle(title);
        news.setContent(content);
        news.setDescription(description);

        if (file != null && !file.isEmpty()) {
            String url = fileUploadService.saveFile(file);
            news.setThumbnail(url);
            news.setThumbnailUrl(url);
        }

        logService.log(getCurrentUserId(), "UPDATE_NEWS", "NEWS", id);
        return toResponseDTO(newsRepo.save(news));
    }

    private News getEditableNews(Integer id) {
        News news = newsRepo.findById(id)
                .orElseThrow(() -> new RuntimeException("News not found"));

        if (!isAdmin()) {
            if (news.getStatus() != NewsStatus.PENDING ||
                    !news.getCreatedBy().equals(getCurrentUserId())) {
                throw new RuntimeException("CTV chỉ được sửa tin PENDING của chính mình");
            }
        }
        return news;
    }

    // ===================== ADMIN =====================

    @Override
    public List<NewsListDTO> getPending() {
        return newsRepo.findByStatusOrderByCreatedAtDesc(NewsStatus.PENDING)
                .stream()
                .map(this::toListDTO)
                .toList();
    }

    @Override
    public NewsResponseDTO approve(Integer id) {
        News news = newsRepo.findById(id)
                .orElseThrow(() -> new RuntimeException("News not found"));

        if (news.getStatus() != NewsStatus.PENDING) {
            throw new RuntimeException("Chỉ duyệt tin PENDING");
        }

        news.setStatus(NewsStatus.PUBLISHED);
        news.setApprovedBy(getCurrentUserId());
        news.setApprovedAt(LocalDateTime.now());

        return toResponseDTO(newsRepo.save(news));
    }

    @Override
    public NewsResponseDTO reject(Integer id, String reason) {
        News news = newsRepo.findById(id)
                .orElseThrow(() -> new RuntimeException("News not found"));

        if (news.getStatus() != NewsStatus.PENDING) {
            throw new RuntimeException("Chỉ từ chối tin PENDING");
        }

        news.setStatus(NewsStatus.REJECTED);
        return toResponseDTO(newsRepo.save(news));
    }

    @Override
    public void delete(Integer id) {
        newsRepo.deleteById(id);
        logService.log(getCurrentUserId(), "DELETE_NEWS", "NEWS", id);
    }

    // ===================== MAPPING =====================

    private NewsResponseDTO toResponseDTO(News n) {
        return NewsResponseDTO.builder()
                .id(n.getId())
                .title(n.getTitle())
                .description(n.getDescription())
                .content(n.getContent())
                .thumbnailUrl(n.getThumbnailUrl())
                .categoryId(n.getCategory() != null ? n.getCategory().getId() : null)
                .categoryName(n.getCategory() != null ? n.getCategory().getName() : null)
                .createdAt(n.getCreatedAt() != null
                        ? n.getCreatedAt().format(DATE_FORMAT)
                        : null)
                .build();
    }

    private NewsListDTO toListDTO(News n) {
        return NewsListDTO.builder()
                .id(n.getId())
                .title(n.getTitle())
                .thumbnailUrl(n.getThumbnailUrl())
                .categoryName(n.getCategory() != null ? n.getCategory().getName() : null)
                .createdAt(n.getCreatedAt() != null
                        ? n.getCreatedAt().format(DATE_FORMAT)
                        : null)
                .build();
    }
}
