package com.checkscam.backend.security;

import jakarta.servlet.FilterChain;
import jakarta.servlet.ServletException;
import jakarta.servlet.http.HttpServletRequest;
import jakarta.servlet.http.HttpServletResponse;

import lombok.RequiredArgsConstructor;
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource;
import org.springframework.stereotype.Component;
import org.springframework.web.filter.OncePerRequestFilter;

import java.io.IOException;

@Component
@RequiredArgsConstructor
public class JwtAuthenticationFilter extends OncePerRequestFilter {

    private final JwtUtil jwtUtil;
    private final CustomUserDetailsService userDetailsService;

    @Override
    protected void doFilterInternal(
            HttpServletRequest request,
            HttpServletResponse response,
            FilterChain filterChain) throws ServletException, IOException {

        String uri = request.getRequestURI();
        String method = request.getMethod();

        // ============================
        // PUBLIC API – BYPASS JWT
        // ============================
        if (isPublic(uri, method)) {
            filterChain.doFilter(request, response);
            return;
        }

        String authHeader = request.getHeader("Authorization");

        // ❗ KHÔNG tự trả 401 tại đây
        // Nếu không có token → để Spring Security xử lý
        if (authHeader != null && authHeader.startsWith("Bearer ")) {

            String token = authHeader.substring(7).trim();

            try {
                String email = jwtUtil.extractEmail(token);
                UserDetails user = userDetailsService.loadUserByUsername(email);

                if (jwtUtil.validateToken(token, user)
                        && SecurityContextHolder.getContext().getAuthentication() == null) {

                    UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(
                            user,
                            null,
                            user.getAuthorities());

                    authToken.setDetails(
                            new WebAuthenticationDetailsSource().buildDetails(request));

                    SecurityContextHolder.getContext().setAuthentication(authToken);
                }

            } catch (Exception e) {
                // ❗ TUYỆT ĐỐI KHÔNG trả response ở đây
                // Token lỗi → coi như chưa authenticated
            }
        }

        filterChain.doFilter(request, response);
    }

    // ============================
    // PUBLIC API RULES (FINAL)
    // ============================
    private boolean isPublic(String uri, String method) {

        // AUTH
        if (uri.startsWith("/api/auth"))
            return true;

        // LOOKUP (PUBLIC – NO LOGIN)
        if (uri.equals("/api/lookup") || uri.startsWith("/api/lookup/"))
            return true;

        // AI
        if (uri.startsWith("/api/ai"))
            return true;

        // NEWS – PUBLIC GET
        if ("GET".equals(method)) {

            if (uri.equals("/api/news"))
                return true;

            if (uri.matches("^/api/news/\\d+$"))
                return true;

            if (uri.startsWith("/api/news/latest"))
                return true;
        }

        return false;
    }
}
