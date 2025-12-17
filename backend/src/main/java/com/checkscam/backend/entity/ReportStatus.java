package com.checkscam.backend.entity;

import jakarta.persistence.*;
import lombok.Data;

@Entity
@Table(name = "report_status")
@Data
public class ReportStatus {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    private String name;
}
