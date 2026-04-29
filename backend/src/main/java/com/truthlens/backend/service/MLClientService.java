package com.truthlens.backend.service;

import com.truthlens.backend.dto.AnalyzeResponse;
import com.truthlens.backend.dto.TokenWeight;
import lombok.extern.slf4j.Slf4j;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.*;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.time.Duration;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

@Service
@Slf4j
public class MLClientService {

    private final RestTemplate restTemplate;
    private final String mlServiceBaseUrl;

    public MLClientService(
            @Value("${ml.service.base-url}") String mlServiceBaseUrl,
            @Value("${ml.service.timeout-seconds}") int timeoutSeconds
    ) {
        this.mlServiceBaseUrl = mlServiceBaseUrl;

        // Configure timeouts on RestTemplate
        org.springframework.http.client.SimpleClientHttpRequestFactory factory =
                new org.springframework.http.client.SimpleClientHttpRequestFactory();
        factory.setConnectTimeout((int) Duration.ofSeconds(5).toMillis());
        factory.setReadTimeout((int) Duration.ofSeconds(timeoutSeconds).toMillis());
        this.restTemplate = new RestTemplate(factory);
    }

    /**
     * Calls the FastAPI /predict endpoint and returns a structured response.
     * Throws RuntimeException if ML service is unreachable — caller handles this.
     */
    @SuppressWarnings("unchecked")
    public MLPrediction predict(String text, String inputType) {
        String url = mlServiceBaseUrl + "/predict";

        Map<String, String> body = new HashMap<>();
        body.put("text", text);
        body.put("input_type", inputType);

        HttpHeaders headers = new HttpHeaders();
        headers.setContentType(MediaType.APPLICATION_JSON);
        HttpEntity<Map<String, String>> request = new HttpEntity<>(body, headers);

        try {
            ResponseEntity<Map> response = restTemplate.postForEntity(url, request, Map.class);
            Map<String, Object> responseBody = response.getBody();

            if (responseBody == null) {
                throw new RuntimeException("Empty response from ML service");
            }

            String verdict = (String) responseBody.get("verdict");
            Double confidence = ((Number) responseBody.get("confidence")).doubleValue();

            Map<String, Double> probabilities = new HashMap<>();
            Map<String, Object> rawProbs = (Map<String, Object>) responseBody.get("probabilities");
            if (rawProbs != null) {
                rawProbs.forEach((k, v) -> probabilities.put(k, ((Number) v).doubleValue()));
            }

            List<Map<String, Object>> rawFeatures =
                    (List<Map<String, Object>>) responseBody.get("top_features");
            List<TokenWeight> topFeatures = rawFeatures == null ? List.of() :
                    rawFeatures.stream()
                    .map(f -> new TokenWeight(
                            (String) f.get("word"),
                            ((Number) f.get("weight")).doubleValue()
                    ))
                    .toList();

            return new MLPrediction(verdict, confidence, probabilities, topFeatures);

        } catch (RestClientException e) {
            log.error("ML service call failed: {}", e.getMessage());
            throw new RuntimeException("ML service unavailable. Please try again later.", e);
        }
    }

    // Inner record to hold the ML response cleanly
    public record MLPrediction(
            String verdict,
            Double confidence,
            Map<String, Double> probabilities,
            List<TokenWeight> topFeatures
    ) {}
}