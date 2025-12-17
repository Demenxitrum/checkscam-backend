package com.checkscam.backend.controller;

import com.checkscam.backend.dto.AIRequest;
import com.checkscam.backend.dto.AIResponse;
import com.checkscam.backend.service.AIService;

import lombok.RequiredArgsConstructor;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/api/ai")
@RequiredArgsConstructor
public class AIController {

    private final AIService aiService;

    @PostMapping("/chat")
    public ResponseEntity<AIResponse> chat(@RequestBody AIRequest req) {
        return ResponseEntity.ok(aiService.chat(req));
    }
}
