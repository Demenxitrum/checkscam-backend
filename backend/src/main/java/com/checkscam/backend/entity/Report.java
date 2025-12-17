package com.checkscam.backend.entity;

import jakarta.persistence.*;
import lombok.Data;

import java.time.LocalDateTime;
import java.util.List;

@Entity
@Table(name = "report")
@Data
public class Report {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @Column(name = "info_value")
    private String infoValue;

    private String description;

    @Column(name = "user_email")
    private String userEmail;

    @ManyToOne
    @JoinColumn(name = "type_id")
    private ReportType type;

    @ManyToOne
    @JoinColumn(name = "status_id")
    private ReportStatus status;

    @ManyToOne
    @JoinColumn(name = "risk_level_id")
    private ReportRiskLevel riskLevel;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @OneToMany(mappedBy = "report", cascade = CascadeType.ALL, fetch = FetchType.LAZY)
    private List<ReportEvidence> evidences;
}
