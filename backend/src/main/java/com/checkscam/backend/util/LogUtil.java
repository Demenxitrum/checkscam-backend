package com.checkscam.backend.util;

import org.springframework.security.core.Authentication;
import org.springframework.security.core.context.SecurityContextHolder;
import org.springframework.stereotype.Component;

@Component
public class LogUtil {

    public Integer getCurrentAccountId() {

        Authentication auth = SecurityContextHolder.getContext().getAuthentication();

        if (auth == null || auth.getName() == null)
            return null;

        try {
            return Integer.parseInt(auth.getName()); // nếu bạn dùng email → sửa lại
        } catch (Exception e) {
            return null;
        }
    }
}
