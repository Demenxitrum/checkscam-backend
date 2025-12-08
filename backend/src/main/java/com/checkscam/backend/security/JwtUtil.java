package com.checkscam.backend.security;

import io.jsonwebtoken.*;
import io.jsonwebtoken.security.Keys;
import org.springframework.security.core.userdetails.UserDetails;
import org.springframework.stereotype.Component;

import java.nio.charset.StandardCharsets;
import java.security.Key;
import java.util.Date;

@Component
public class JwtUtil {

    private static final String SECRET = "THIS_IS_A_REAL_256BIT_SECRET_KEY_FOR_JWT_SECURITY_1234567890_ABCDEF";

    private final Key key = Keys.hmacShaKeyFor(SECRET.getBytes(StandardCharsets.UTF_8));

    private final long ACCESS_EXP = 1000 * 60 * 15; // 15 phút
    private final long REFRESH_EXP = 1000 * 60 * 60 * 24 * 7; // 7 ngày

    // ======================
    // CREATE TOKEN
    // ======================
    public String generateAccessToken(String email, String role) {
        return generateToken(email.toLowerCase(), role, ACCESS_EXP);
    }

    public String generateRefreshToken(String email, String role) {
        return generateToken(email.toLowerCase(), role, REFRESH_EXP);
    }

    private String generateToken(String email, String role, long exp) {
        return Jwts.builder()
                .setSubject(email.toLowerCase())
                .claim("role", "ROLE_" + role)
                .setIssuedAt(new Date())
                .setExpiration(new Date(System.currentTimeMillis() + exp))
                .signWith(key, SignatureAlgorithm.HS256)
                .compact();
    }

    // ======================
    // VALIDATE (NO USERDETAILS)
    // ======================
    public boolean validateToken(String token) {
        try {
            Claims claims = extractAllClaims(token);
            return !claims.getExpiration().before(new Date());
        } catch (Exception e) {
            return false;
        }
    }

    // ======================
    // VALIDATE WITH USERDETAILS
    // (dùng trong Filter)
    // ======================
    public boolean validateToken(String token, UserDetails userDetails) {
        try {
            String username = extractEmail(token);
            return username.equalsIgnoreCase(userDetails.getUsername())
                    && !isExpired(token);
        } catch (Exception e) {
            return false;
        }
    }

    // ======================
    // EXTRACT
    // ======================
    public String extractEmail(String token) {
        return extractAllClaims(token).getSubject();
    }

    public String extractRole(String token) {
        return extractAllClaims(token).get("role", String.class);
    }

    public Date extractExpiration(String token) {
        return extractAllClaims(token).getExpiration();
    }

    private boolean isExpired(String token) {
        return extractExpiration(token).before(new Date());
    }

    private Claims extractAllClaims(String token) {
        return Jwts.parserBuilder()
                .setSigningKey(key)
                .build()
                .parseClaimsJws(token.trim())
                .getBody();
    }
}
