package com.truthlens.backend.controller;

import com.truthlens.backend.dto.AnalyzeRequest;
import com.truthlens.backend.dto.AnalyzeResponse;
import com.truthlens.backend.service.AnalysisService;
import jakarta.validation.Valid;
import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;

@RestController
@RequestMapping("/api")
@RequiredArgsConstructor
@CrossOrigin(origins = {"http://localhost:5173", "http://localhost:3000"})
public class AnalysisController {

    private final AnalysisService analysisService;

    /**
     * POST /api/analyze
     * Main endpoint — accepts text, returns verdict + explanation
     */
    @PostMapping("/analyze")
    public ResponseEntity<AnalyzeResponse> analyze(@Valid @RequestBody AnalyzeRequest request) {
        AnalyzeResponse response = analysisService.analyze(
                request.getText(),
                request.getInputType()
        );
        return ResponseEntity.ok(response);
    }

    /**
     * GET /api/history
     * Returns all past analyses, newest first
     */
    @GetMapping("/history")
    public ResponseEntity<List<AnalyzeResponse>> history() {
        return ResponseEntity.ok(analysisService.getHistory());
    }

    /**
     * GET /api/health
     * Quick liveness check
     */
    @GetMapping("/health")
    public ResponseEntity<String> health() {
        return ResponseEntity.ok("TruthLens backend is running.");
    }
}