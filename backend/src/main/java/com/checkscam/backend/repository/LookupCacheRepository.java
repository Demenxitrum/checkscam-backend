package com.checkscam.backend.repository;

import com.checkscam.backend.entity.LookupCache;
import com.checkscam.backend.entity.LookupCacheType;
import org.springframework.data.jpa.repository.JpaRepository;

public interface LookupCacheRepository extends JpaRepository<LookupCache, Integer> {

    LookupCache findByTypeAndValue(LookupCacheType type, String value);
}
