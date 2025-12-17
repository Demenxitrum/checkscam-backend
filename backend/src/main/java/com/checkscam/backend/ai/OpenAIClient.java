package com.checkscam.backend.ai;

import com.theokanning.openai.completion.chat.ChatCompletionRequest;
import com.theokanning.openai.completion.chat.ChatMessage;
import com.theokanning.openai.completion.chat.ChatCompletionChoice;
import com.theokanning.openai.service.OpenAiService;

import org.springframework.stereotype.Component;
import java.time.Duration;
import java.util.List;

@Component
public class OpenAIClient {

    private final OpenAiService service;

    public OpenAIClient() {
        String apiKey = System.getenv("OPENAI_API_KEY");

        this.service = new OpenAiService(apiKey, Duration.ofSeconds(60));
    }

    public String ask(String prompt) {

        ChatMessage systemMessage = new ChatMessage(
                "system",
                "Bạn là trợ lý AI chống lừa đảo. Giải thích dễ hiểu và chính xác.");

        ChatMessage userMessage = new ChatMessage("user", prompt);

        ChatCompletionRequest req = ChatCompletionRequest.builder()
                .model("gpt-4o-mini")
                .messages(List.of(systemMessage, userMessage))
                .maxTokens(400)
                .temperature(0.7)
                .build();

        List<ChatCompletionChoice> choices = service.createChatCompletion(req).getChoices();

        return choices.get(0).getMessage().getContent();
    }
}
