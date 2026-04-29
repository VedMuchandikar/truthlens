package com.truthlens.backend.dto;

import jakarta.validation.constraints.NotBlank;
import jakarta.validation.constraints.Size;
import lombok.Data;

@Data
public class AnalyzeRequest {

    @NotBlank(message = "Text cannot be blank")
    @Size(min = 3, max = 10000, message = "Text must be between 3 and 10000 characters")
    private String text;

    private String inputType = "TEXT"; // TEXT | URL | EMAIL | WHATSAPP
}