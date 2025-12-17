package com.checkscam.backend.service;

import com.checkscam.backend.dto.AIRequest;
import com.checkscam.backend.dto.AIResponse;

public interface AIService {
    AIResponse chat(AIRequest request);
}
