package com.checkscam.backend.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "report_evidence")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class ReportEvidence {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @ManyToOne
    @JoinColumn(name = "report_id")
    private Report report;

    @Column(name = "file_path")
    private String filePath;
}
