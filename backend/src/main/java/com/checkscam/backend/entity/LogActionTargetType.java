package com.checkscam.backend.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "log_action_target_type")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class LogActionTargetType {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    private String name; // ACCOUNT, REPORT, NEWS...
}
