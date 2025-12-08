package com.checkscam.backend.entity;

import jakarta.persistence.*;
import lombok.*;

@Entity
@Table(name = "account_status")
@Data
@NoArgsConstructor
@AllArgsConstructor
public class AccountStatus {

    @Id
    private Integer id; // Bảng này KHÔNG auto increment

    @Column(nullable = false, unique = true)
    private String name;
}
