package com.checkscam.backend.service.impl;

import com.checkscam.backend.dto.*;
import com.checkscam.backend.entity.Account;
import com.checkscam.backend.entity.AccountRole;
import com.checkscam.backend.entity.AccountStatus;
import com.checkscam.backend.repository.AccountRepository;
import com.checkscam.backend.repository.AccountRoleRepository;
import com.checkscam.backend.repository.AccountStatusRepository;
import com.checkscam.backend.security.JwtUtil;
import com.checkscam.backend.service.AuthService;
import com.checkscam.backend.service.LogActionService;

import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.userdetails.UsernameNotFoundException;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
@RequiredArgsConstructor
public class AuthServiceImpl implements AuthService {

    private final AuthenticationManager authManager;
    private final AccountRepository accountRepo;
    private final AccountRoleRepository roleRepo;
    private final AccountStatusRepository statusRepo;
    private final PasswordEncoder encoder;
    private final JwtUtil jwtUtil;
    private final LogActionService logService;

    // =====================================================
    // LOGIN
    // =====================================================
    @Override
    public TokenResponse login(LoginRequest req) {

        // Xác thực username + password
        authManager.authenticate(
                new UsernamePasswordAuthenticationToken(
                        req.getEmail(),
                        req.getPassword()));

        // Lấy account từ DB
        Account acc = accountRepo.findByEmail(req.getEmail())
                .orElseThrow(() -> new UsernameNotFoundException("Account not found"));

        String role = acc.getRole().getName();

        String accessToken = jwtUtil.generateAccessToken(acc.getEmail(), role);
        String refreshToken = jwtUtil.generateRefreshToken(acc.getEmail(), role);

        logService.log(acc.getId(), "LOGIN", "ACCOUNT", acc.getId());

        return TokenResponse.builder()
                .accessToken(accessToken)
                .refreshToken(refreshToken)
                .role(role)
                .build();
    }

    // =====================================================
    // REGISTER
    // =====================================================
    @Override
    public void register(RegisterRequest req) {

        if (accountRepo.existsByEmail(req.getEmail())) {
            throw new RuntimeException("Email already exists");
        }

        AccountRole userRole = roleRepo.findByName("USER")
                .orElseThrow(() -> new RuntimeException("Missing USER role"));

        AccountStatus active = statusRepo.findById(1)
                .orElseThrow(() -> new RuntimeException("Missing ACTIVE status"));

        Account acc = new Account();
        acc.setEmail(req.getEmail());
        acc.setName(req.getName());
        acc.setPassword(encoder.encode(req.getPassword()));
        acc.setRole(userRole);
        acc.setStatus(active);
        acc.setCreatedAt(java.time.LocalDateTime.now());

        accountRepo.save(acc);

        logService.log(acc.getId(), "REGISTER", "ACCOUNT", acc.getId());
    }

    // =====================================================
    // REFRESH TOKEN
    // =====================================================
    @Override
    public TokenResponse refresh(String refreshToken) {

        if (!jwtUtil.validateToken(refreshToken)) {
            throw new RuntimeException("Invalid refresh token");
        }

        String email = jwtUtil.extractEmail(refreshToken);

        Account acc = accountRepo.findByEmail(email)
                .orElseThrow(() -> new UsernameNotFoundException("Account not found"));

        String role = acc.getRole().getName();

        String newAccess = jwtUtil.generateAccessToken(email, role);
        String newRefresh = jwtUtil.generateRefreshToken(email, role);

        return TokenResponse.builder()
                .accessToken(newAccess)
                .refreshToken(newRefresh)
                .role(role)
                .build();
    }
}
