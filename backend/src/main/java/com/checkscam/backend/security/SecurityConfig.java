package com.checkscam.backend.security;

import lombok.RequiredArgsConstructor;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.HttpMethod;
import org.springframework.security.authentication.AuthenticationManager;
import org.springframework.security.authentication.dao.DaoAuthenticationProvider;
import org.springframework.security.config.annotation.authentication.configuration.AuthenticationConfiguration;

import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity;
import org.springframework.security.config.annotation.web.builders.HttpSecurity;

import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity;
import org.springframework.security.config.http.SessionCreationPolicy;

import org.springframework.security.crypto.bcrypt.BCryptPasswordEncoder;
import org.springframework.security.crypto.password.PasswordEncoder;

import org.springframework.security.web.AuthenticationEntryPoint;
import org.springframework.security.web.SecurityFilterChain;
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter;

@Configuration
@EnableWebSecurity
@EnableMethodSecurity
@RequiredArgsConstructor
public class SecurityConfig {

    private final JwtAuthenticationFilter jwtAuthFilter;
    private final CustomUserDetailsService userDetailsService;

    @Bean
    public SecurityFilterChain filterChain(HttpSecurity http) throws Exception {

        http.csrf(cs -> cs.disable());
        http.cors(cors -> cors.disable());

        http.sessionManagement(session -> session.sessionCreationPolicy(SessionCreationPolicy.STATELESS));

        http.authorizeHttpRequests(auth -> auth

                // ================================
                // PUBLIC API
                // ================================
                .requestMatchers("/api/auth/**").permitAll()
                .requestMatchers("/api/lookup/**").permitAll()
                .requestMatchers("/api/ai/**").permitAll()
                .requestMatchers(HttpMethod.GET, "/api/news/**").permitAll()

                // ================================
                // ADMIN + CTV
                // ================================
                // Dashboard (CTV & Admin)
                .requestMatchers("/api/dashboard/**").hasAnyRole("ADMIN", "CTV")

                // News: tạo + sửa (CTV & Admin)
                .requestMatchers(HttpMethod.POST, "/api/news/**").hasAnyRole("ADMIN", "CTV")
                .requestMatchers(HttpMethod.PUT, "/api/news/**").hasAnyRole("ADMIN", "CTV")

                // Report: duyệt / từ chối / cập nhật (CTV & Admin)
                .requestMatchers(HttpMethod.PUT, "/api/report/**").hasAnyRole("ADMIN", "CTV")
                .requestMatchers(HttpMethod.GET, "/api/report/**").hasAnyRole("ADMIN", "CTV")

                // ================================
                // ADMIN ONLY
                // ================================
                // Quản lý account
                .requestMatchers("/api/account/**").hasRole("ADMIN")

                // News: xóa
                .requestMatchers(HttpMethod.DELETE, "/api/news/**").hasRole("ADMIN")

                // Report: xóa
                .requestMatchers(HttpMethod.DELETE, "/api/report/**").hasRole("ADMIN")

                // ================================
                // USER + CTV + ADMIN
                // ================================
                // Gửi báo cáo
                .requestMatchers(HttpMethod.POST, "/api/report/**").authenticated()

                // ================================
                // MẶC ĐỊNH: CẦN LOGIN
                // ================================
                .anyRequest().authenticated());

        http.exceptionHandling(ex -> ex
                .authenticationEntryPoint(unauthorizedHandler()));

        http.authenticationProvider(authProvider());

        http.addFilterBefore(jwtAuthFilter, UsernamePasswordAuthenticationFilter.class);

        return http.build();
    }

    @Bean
    public AuthenticationEntryPoint unauthorizedHandler() {
        return (req, res, ex) -> {
            res.setStatus(401);
            res.setContentType("application/json");
            res.getWriter().write("{\"error\":\"Unauthorized\"}");
        };
    }

    @Bean
    public DaoAuthenticationProvider authProvider() {
        DaoAuthenticationProvider provider = new DaoAuthenticationProvider();
        provider.setUserDetailsService(userDetailsService);
        provider.setPasswordEncoder(passwordEncoder());
        return provider;
    }

    @Bean
    public AuthenticationManager authManager(AuthenticationConfiguration config) throws Exception {
        return config.getAuthenticationManager();
    }

    @Bean
    public PasswordEncoder passwordEncoder() {
        return new BCryptPasswordEncoder();
    }
}
