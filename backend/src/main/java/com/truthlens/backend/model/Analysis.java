package com.truthlens.backend.model;

import jakarta.persistence.*;
import lombok.Data;
import lombok.NoArgsConstructor;
import lombok.AllArgsConstructor;
import lombok.Builder;
import java.time.LocalDateTime;

@Entity
@Table(name = "analyses")
@Data
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class Analysis {

    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;

    @Column(columnDefinition = "TEXT", nullable = false)
    private String inputText;

    @Column(nullable = false)
    private String inputType; // TEXT, URL, EMAIL, WHATSAPP

    @Column(nullable = false)
    private String verdict; // GENUINE, SCAM, SUSPICIOUS

    @Column(nullable = false)
    private Double confidence;

    @Column(columnDefinition = "TEXT")
    private String topFeaturesJson; // store raw JSON string for Phase 1

    @Column(nullable = false)
    private LocalDateTime createdAt;

    @PrePersist
    protected void onCreate() {
        createdAt = LocalDateTime.now();
    }
}