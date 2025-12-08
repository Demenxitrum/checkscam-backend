package com.checkscam.backend.service.impl;

import com.checkscam.backend.ai.OpenAIClient;
import com.checkscam.backend.dto.AIRequest;
import com.checkscam.backend.dto.AIResponse;
import com.checkscam.backend.dto.LookupResponse;
import com.checkscam.backend.service.AIService;
import com.checkscam.backend.service.LookupService;

import lombok.RequiredArgsConstructor;
import org.springframework.stereotype.Service;

import java.util.regex.Matcher;
import java.util.regex.Pattern;

@Service
@RequiredArgsConstructor
public class AIServiceImpl implements AIService {

        private final LookupService lookupService;
        private final OpenAIClient openAIClient;

        // ==========================
        // REGEX PATTERNS
        // ==========================
        private static final Pattern PHONE_PATTERN = Pattern.compile("\\b0\\d{9}\\b");
        private static final Pattern BANK_PATTERN = Pattern.compile("\\b\\d{6,16}\\b"); // tài khoản ngân hàng phổ biến
        private static final Pattern URL_PATTERN = Pattern.compile("(https?://[^\\s]+)");

        @Override
        public AIResponse chat(AIRequest req) {
                String msg = req.getMessage().trim();

                // ==========================
                // 1) Detect URL trước (ưu tiên nhất)
                // ==========================
                Matcher urlMatcher = URL_PATTERN.matcher(msg);
                if (urlMatcher.find()) {
                        String url = urlMatcher.group(1);

                        LookupResponse lookup = lookupService.lookupURL(url);

                        String reply = openAIClient.ask(
                                        "User hỏi: " + msg +
                                                        "\nDữ liệu URL tra cứu: " + lookup +
                                                        "\nHãy phân tích mức độ rủi ro và đưa ra lời khuyên chống lừa đảo.");

                        return AIResponse.builder()
                                        .reply(reply)
                                        .hasLookup(true)
                                        .lookupType("URL")
                                        .lookupValue(url)
                                        .reportCount(lookup.getReportCount())
                                        .riskLevel(lookup.getRiskLevel())
                                        .build();
                }

                // ==========================
                // 2) Detect Phone (bắt buộc phải bắt đầu bằng 0)
                // ==========================
                Matcher phoneMatcher = PHONE_PATTERN.matcher(msg);
                if (phoneMatcher.find()) {
                        String phone = phoneMatcher.group();

                        LookupResponse lookup = lookupService.lookupPhone(phone);

                        String reply = openAIClient.ask(
                                        "Số điện thoại được người dùng đề cập: " + phone +
                                                        "\nThông tin tra cứu: " + lookup +
                                                        "\nUser hỏi: " + msg +
                                                        "\nHãy trả lời rõ ràng, dễ hiểu và cảnh báo rủi ro nếu có.");

                        return AIResponse.builder()
                                        .reply(reply)
                                        .hasLookup(true)
                                        .lookupType("PHONE")
                                        .lookupValue(phone)
                                        .reportCount(lookup.getReportCount())
                                        .riskLevel(lookup.getRiskLevel())
                                        .build();
                }

                // ==========================
                // 3) Detect BANK (nếu chứa 6 - 16 số liên tục)
                // ==========================
                Matcher bankMatcher = BANK_PATTERN.matcher(msg);
                if (bankMatcher.find()) {
                        String bankAcc = bankMatcher.group();

                        LookupResponse lookup = lookupService.lookupBank(bankAcc);

                        String reply = openAIClient.ask(
                                        "Thông tin STK được đề cập: " + bankAcc +
                                                        "\nKết quả tra cứu chống lừa đảo: " + lookup +
                                                        "\nUser hỏi: " + msg +
                                                        "\nHãy giải thích chi tiết mức độ an toàn.");

                        return AIResponse.builder()
                                        .reply(reply)
                                        .hasLookup(true)
                                        .lookupType("BANK")
                                        .lookupValue(bankAcc)
                                        .reportCount(lookup.getReportCount())
                                        .riskLevel(lookup.getRiskLevel())
                                        .build();
                }

                // ==========================
                // 4) Không có dữ liệu tra cứu → AI thuần
                // ==========================
                String reply = openAIClient.ask(
                                "User hỏi: " + msg +
                                                "\nHãy trả lời tự nhiên, dễ hiểu và đưa ra lời khuyên an toàn khi cần.");

                return AIResponse.builder()
                                .reply(reply)
                                .hasLookup(false)
                                .build();
        }
}
