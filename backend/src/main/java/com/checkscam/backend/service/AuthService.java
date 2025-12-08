package com.checkscam.backend.service;

import com.checkscam.backend.dto.LoginRequest;
import com.checkscam.backend.dto.RegisterRequest;
import com.checkscam.backend.dto.TokenResponse;

public interface AuthService {
    TokenResponse login(LoginRequest req);

    TokenResponse refresh(String refreshToken);

    void register(RegisterRequest req);
}
