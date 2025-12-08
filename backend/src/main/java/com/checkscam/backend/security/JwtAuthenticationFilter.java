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

        // Các endpoint public = bỏ qua JWT
        if (isPublic(uri, method)) {
            filterChain.doFilter(request, response);
            return;
        }

        String authHeader = request.getHeader("Authorization");

        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            filterChain.doFilter(request, response);
            return;
        }

        // Token chuẩn (fix ký tự ẩn, khoảng trắng)
        String token = authHeader.substring(7).trim();

        String email;
        try {
            email = jwtUtil.extractEmail(token);
        } catch (Exception e) {
            returnUnauthorized(response, "Invalid token");
            return;
        }

        UserDetails user = userDetailsService.loadUserByUsername(email);

        if (!jwtUtil.validateToken(token, user)) {
            returnUnauthorized(response, "Token invalid or expired");
            return;
        }

        if (SecurityContextHolder.getContext().getAuthentication() == null) {

            UsernamePasswordAuthenticationToken authToken = new UsernamePasswordAuthenticationToken(
                    user,
                    null,
                    user.getAuthorities());

            authToken.setDetails(
                    new WebAuthenticationDetailsSource().buildDetails(request));

            SecurityContextHolder.getContext().setAuthentication(authToken);
        }

        filterChain.doFilter(request, response);
    }

    private boolean isPublic(String uri, String method) {

        if (uri.startsWith("/api/auth/"))
            return true;
        if (uri.startsWith("/api/lookup/"))
            return true;
        if (uri.startsWith("/api/ai/"))
            return true;
        if (uri.startsWith("/api/news/") && method.equals("GET"))
            return true;

        return false;
    }

    private void returnUnauthorized(HttpServletResponse response, String msg) throws IOException {
        response.setStatus(401);
        response.setContentType("application/json");
        response.getWriter().write("{\"error\": \"" + msg + "\"}");
    }
}
