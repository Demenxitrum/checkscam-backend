package com.checkscam.backend.repository;

import com.checkscam.backend.entity.NewsCategory;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;

import java.util.Optional;

@Repository
public interface NewsCategoryRepository extends JpaRepository<NewsCategory, Integer> {
    Optional<NewsCategory> findByName(String name);
}
