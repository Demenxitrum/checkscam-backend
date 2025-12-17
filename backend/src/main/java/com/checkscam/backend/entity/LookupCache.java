package com.checkscam.backend.entity;

import jakarta.persistence.*;
import lombok.*;

import java.time.LocalDateTime;

@Entity
@Table(name = "lookup_cache")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LookupCache {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @ManyToOne
    @JoinColumn(name = "type_id")
    private LookupCacheType type;

    private String value;

    @Column(name = "report_count")
    private int reportCount;

    @ManyToOne
    @JoinColumn(name = "risk_level_id")
    private ReportRiskLevel riskLevel;

    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
}
