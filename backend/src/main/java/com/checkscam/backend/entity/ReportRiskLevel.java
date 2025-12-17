package com.checkscam.backend.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "report_risk_level")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class ReportRiskLevel {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    private String name;
}
