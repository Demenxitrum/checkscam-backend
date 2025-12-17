package com.checkscam.backend.entity;

import jakarta.persistence.*;
import lombok.Data;

@Entity
@Table(name = "report_type")
@Data
public class ReportType {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    private String name;
}
