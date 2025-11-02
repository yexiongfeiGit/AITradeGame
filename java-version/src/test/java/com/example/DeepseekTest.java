package com.example;

import org.junit.jupiter.api.Test;
import org.springframework.ai.deepseek.DeepSeekChatModel;
import org.springframework.ai.deepseek.DeepSeekChatOptions;
import org.springframework.ai.deepseek.api.DeepSeekApi;

public class DeepseekTest {

    public static void main(String[] args) {
        DeepSeekApi.Builder builder = DeepSeekApi.builder().apiKey("sk-d9df3085cf3941fdbbaaeb7e41ba20ec");

        DeepSeekChatModel deepSeekChatModel = DeepSeekChatModel.builder()
                .deepSeekApi(builder.build())
                .defaultOptions(DeepSeekChatOptions.builder()
                        .model("deepseek-chat-3.5")
                        .build())
                .build();

        // 调用模型
        String response = deepSeekChatModel.call("你好");
        System.out.println(response);
    }
}
