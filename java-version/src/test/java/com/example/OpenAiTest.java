package com.example;

import org.junit.jupiter.api.Test;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.openai.OpenAiChatModel;
import org.springframework.ai.openai.OpenAiChatOptions;
import org.springframework.ai.openai.api.OpenAiApi;
import org.springframework.ai.openai.OpenAiChatModel;

public class OpenAiTest {

    public static void main(String[] args) {

        OpenAiApi.Builder builder = OpenAiApi.builder()
                .baseUrl("https://openrouter.ai/api/v1")
                .apiKey("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");

        OpenAiApi openAiApi = builder.build();
        OpenAiChatModel openAiChatModel = OpenAiChatModel.builder()
                .openAiApi(openAiApi)
                .defaultOptions(OpenAiChatOptions.builder()
                        .model("gpt-3.5-turbo")
                        .build())
                .build();

        ChatClient chatClient = ChatClient.builder(openAiChatModel).build();
        String response = chatClient.prompt("你是哪个模型").call().content();
        System.out.println("-----------------");
        System.out.println(response);

    }
}