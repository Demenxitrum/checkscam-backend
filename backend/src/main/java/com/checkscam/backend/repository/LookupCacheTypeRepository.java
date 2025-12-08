package com.checkscam.backend.repository;

import com.checkscam.backend.entity.LookupCacheType;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface LookupCacheTypeRepository extends JpaRepository<LookupCacheType, Integer> {

    Optional<LookupCacheType> findByName(String name);
}
