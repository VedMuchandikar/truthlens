package com.truthlens.backend.service;

import com.fasterxml.jackson.core.JsonProcessingException;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.truthlens.backend.dto.AnalyzeResponse;
import com.truthlens.backend.model.Analysis;
import com.truthlens.backend.repository.AnalysisRepository;
import lombok.RequiredArgsConstructor;
import lombok.extern.slf4j.Slf4j;
import org.springframework.stereotype.Service;

import java.util.List;
import java.util.stream.Collectors;

@Service
@RequiredArgsConstructor
@Slf4j
public class AnalysisService {

    private final MLClientService mlClientService;
    private final AnalysisRepository analysisRepository;
    private final ObjectMapper objectMapper;

    public AnalyzeResponse analyze(String text, String inputType) {
        // 1. Call ML service
        MLClientService.MLPrediction prediction = mlClientService.predict(text, inputType);

        // 2. Serialize top features to JSON string for storage
        String featuresJson = "[]";
        try {
            featuresJson = objectMapper.writeValueAsString(prediction.topFeatures());
        } catch (JsonProcessingException e) {
            log.warn("Could not serialize top features: {}", e.getMessage());
        }

        // 3. Persist to H2
        Analysis saved = analysisRepository.save(
                Analysis.builder()
                        .inputText(text)
                        .inputType(inputType)
                        .verdict(prediction.verdict())
                        .confidence(prediction.confidence())
                        .topFeaturesJson(featuresJson)
                        .build()
        );

        log.info("Analysis saved: id={} verdict={} confidence={}",
                saved.getId(), saved.getVerdict(), saved.getConfidence());

        // 4. Build response
        return AnalyzeResponse.builder()
                .id(saved.getId())
                .verdict(saved.getVerdict())
                .confidence(saved.getConfidence())
                .probabilities(prediction.probabilities())
                .topFeatures(prediction.topFeatures())
                .inputType(saved.getInputType())
                .analyzedAt(saved.getCreatedAt())
                .build();
    }

    public List<AnalyzeResponse> getHistory() {
        return analysisRepository.findAllByOrderByCreatedAtDesc()
                .stream()
                .map(a -> AnalyzeResponse.builder()
                        .id(a.getId())
                        .verdict(a.getVerdict())
                        .confidence(a.getConfidence())
                        .inputType(a.getInputType())
                        .analyzedAt(a.getCreatedAt())
                        .build())
                .collect(Collectors.toList());
    }
}