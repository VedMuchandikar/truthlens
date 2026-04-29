package com.truthlens.backend.dto;

import lombok.Data;
import lombok.Builder;
import lombok.AllArgsConstructor;
import lombok.NoArgsConstructor;
import java.time.LocalDateTime;
import java.util.List;
import java.util.Map;

@Data
@Builder
@AllArgsConstructor
@NoArgsConstructor
public class AnalyzeResponse {
    private Long id;
    private String verdict;
    private Double confidence;
    private Map<String, Double> probabilities;
    private List<TokenWeight> topFeatures;
    private String inputType;
    private LocalDateTime analyzedAt;
}