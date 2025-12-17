package com.checkscam.backend.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "news_category")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class NewsCategory {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    private String name;
}
