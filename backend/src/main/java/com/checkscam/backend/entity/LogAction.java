package com.checkscam.backend.entity;

import jakarta.persistence.*;
import lombok.*;
import java.time.LocalDateTime;

@Entity
@Table(name = "log_action")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class LogAction {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Integer id;

    @ManyToOne
    @JoinColumn(name = "account_id")
    private Account account;

    private String action;

    @ManyToOne
    @JoinColumn(name = "target_type_id")
    private LogActionTargetType targetType;

    @Column(name = "target_id")
    private Integer targetId;

    @Column(name = "created_at")
    private LocalDateTime createdAt;

    @PrePersist
    public void prePersist() {
        if (createdAt == null) {
            createdAt = LocalDateTime.now();
        }
    }
}
