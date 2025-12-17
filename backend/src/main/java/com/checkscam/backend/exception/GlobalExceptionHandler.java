package com.checkscam.backend.exception;

import io.jsonwebtoken.ExpiredJwtException;
import io.jsonwebtoken.JwtException;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.security.access.AccessDeniedException;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.bind.MissingServletRequestParameterException;
import org.springframework.web.bind.annotation.ExceptionHandler;
import org.springframework.web.bind.annotation.RestControllerAdvice;

import java.time.LocalDateTime;
import java.util.HashMap;
import java.util.Map;

@RestControllerAdvice
public class GlobalExceptionHandler {

    // ===============================
    // 1. PARAMETER MISSING ?value=
    // ===============================
    @ExceptionHandler(MissingServletRequestParameterException.class)
    public ResponseEntity<?> handleMissingParameter(MissingServletRequestParameterException ex) {

        return build(HttpStatus.BAD_REQUEST,
                "Missing parameter: " + ex.getParameterName());
    }

    // ===============================
    // 2. VALIDATION ERROR (@Valid)
    // ===============================
    @ExceptionHandler(MethodArgumentNotValidException.class)
    public ResponseEntity<?> handleValidation(MethodArgumentNotValidException ex) {

        String msg = ex.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(f -> f.getField() + ": " + f.getDefaultMessage())
                .findFirst()
                .orElse("Invalid request");

        return build(HttpStatus.BAD_REQUEST, msg);
    }

    // ===============================
    // 3. JWT EXPIRED
    // ===============================
    @ExceptionHandler(ExpiredJwtException.class)
    public ResponseEntity<?> handleExpiredJwt(ExpiredJwtException ex) {
        return build(HttpStatus.UNAUTHORIZED, "Token expired");
    }

    // ===============================
    // 4. JWT INVALID
    // ===============================
    @ExceptionHandler(JwtException.class)
    public ResponseEntity<?> handleJwt(JwtException ex) {
        return build(HttpStatus.UNAUTHORIZED, "Invalid token");
    }

    // ===============================
    // 5. FORBIDDEN (NO PERMISSION)
    // ===============================
    @ExceptionHandler(AccessDeniedException.class)
    public ResponseEntity<?> handleAccessDenied(AccessDeniedException ex) {

        return build(HttpStatus.FORBIDDEN, "Access denied");
    }

    // ===============================
    // 6. RUNTIME EXCEPTION
    // ===============================
    @ExceptionHandler(RuntimeException.class)
    public ResponseEntity<?> handleRuntime(RuntimeException ex) {

        return build(HttpStatus.BAD_REQUEST, ex.getMessage());
    }

    // ===============================
    // 7. ALL OTHER ERRORS (500)
    // ===============================
    @ExceptionHandler(Exception.class)
    public ResponseEntity<?> handleException(Exception ex) {

        return build(HttpStatus.INTERNAL_SERVER_ERROR,
                "Internal server error: " + ex.getMessage());
    }

    // ===============================
    // HELPER: Build JSON response
    // ===============================
    private ResponseEntity<Map<String, Object>> build(HttpStatus status, String message) {

        Map<String, Object> body = new HashMap<>();
        body.put("status", status.value());
        body.put("error", status.getReasonPhrase());
        body.put("message", message);
        body.put("timestamp", LocalDateTime.now().toString());

        return ResponseEntity.status(status).body(body);
    }
}
