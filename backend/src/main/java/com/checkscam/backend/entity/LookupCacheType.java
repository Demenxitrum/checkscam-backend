package com.checkscam.backend.entity;

import jakarta.persistence.*;
import lombok.Data;

@Entity
@Table(name = "lookup_cache_type")
@Data
public class LookupCacheType {

    @Id
    private Integer id;

    private String name; // PHONE / BANK / URL
}
