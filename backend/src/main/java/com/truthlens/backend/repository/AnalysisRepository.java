package com.truthlens.backend.repository;

import com.truthlens.backend.model.Analysis;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import java.util.List;

@Repository
public interface AnalysisRepository extends JpaRepository<Analysis, Long> {
    List<Analysis> findAllByOrderByCreatedAtDesc();
}