package com.checkscam.backend.repository;

import com.checkscam.backend.entity.News;
import org.springframework.data.domain.Page;
import org.springframework.data.domain.Pageable;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.List;

@Repository
public interface NewsRepository extends JpaRepository<News, Integer> {

    Page<News> findByCategory_IdAndTitleContainingIgnoreCase(Integer categoryId, String keyword, Pageable pageable);

    Page<News> findByCategory_Id(Integer categoryId, Pageable pageable);

    Page<News> findByTitleContainingIgnoreCase(String keyword, Pageable pageable);

    List<News> findTop5ByOrderByCreatedAtDesc();
}
