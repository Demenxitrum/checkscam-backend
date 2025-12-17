package com.checkscam.backend.repository;

import com.checkscam.backend.entity.LookupCache;
import com.checkscam.backend.entity.LookupCacheType;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;

public interface LookupCacheRepository extends JpaRepository<LookupCache, Integer> {

    /**
     * ===== EXISTING METHOD (GIỮ NGUYÊN – KHÔNG ĐỤNG) =====
     * Dùng cho các API hiện tại
     */
    LookupCache findByTypeAndValue(LookupCacheType type, String value);

    /**
     * ===== NEW METHOD (CHỈ PHỤC VỤ ADMIN) =====
     * Tra cứu theo type name + value
     * READ-ONLY
     */
    Optional<LookupCache> findByValueAndType_Name(
            String value,
            String typeName
    );
}
