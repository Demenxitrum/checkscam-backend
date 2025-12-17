package com.checkscam.backend.repository;

import com.checkscam.backend.entity.News;
import com.checkscam.backend.entity.enums.NewsStatus;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.List;

public interface NewsRepository extends JpaRepository<News, Integer> {

    // ===================== PUBLIC =====================

    Page<News> findByStatus(
            NewsStatus status, Pageable pageable);

    Page<News> findByStatusAndCategory_Id(
            NewsStatus status, Integer categoryId, Pageable pageable);

    Page<News> findByStatusAndTitleContainingIgnoreCase(
            NewsStatus status, String keyword, Pageable pageable);

    Page<News> findByStatusAndCategory_IdAndTitleContainingIgnoreCase(
            NewsStatus status, Integer categoryId, String keyword, Pageable pageable);

    List<News> findTop5ByStatusOrderByCreatedAtDesc(
            NewsStatus status);

    // ===================== ADMIN =====================

    List<News> findByStatusOrderByCreatedAtDesc(
            NewsStatus status);
}
