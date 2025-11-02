package com.example.config;

import org.springframework.ai.chat.client.ChatClient;
import org.springframework.ai.openai.OpenAiChatModel;
import org.springframework.ai.openai.OpenAiChatOptions;
import org.springframework.ai.openai.api.OpenAiApi;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Conditional;
import org.springframework.context.annotation.Configuration;

/**
 * AI配置类，用于配置与OpenAI API相关的Bean
 * 
 * 该类定义了与OpenAI集成所需的Bean，包括OpenAiApi和OpenAiChatModel。
 * 使用条件注解确保只有在满足特定条件时才会创建这些Bean。
 */
@Configuration
public class AIConfig {

    /**
     * 从application.properties或环境变量中注入OpenAI API密钥
     * 
     * 该值将在OpenAiApiCondition类中被检查，以确定是否应该创建AI相关的Bean。
     */
    @Value("${openai.api.key}")
    private String apiKey;

    /**
     * 创建OpenAiApi Bean，用于与OpenAI API进行通信
     * 
     * 该Bean仅在满足OpenAiApiCondition条件时创建：
     * - 环境变量中存在"openai.api.key"
     * - 该密钥不为空
     * - 该密钥不是默认占位符值
     * 
     * @return OpenAiApi实例
     */
    @Bean
    @Conditional(OpenAiApiCondition.class)
    public OpenAiApi openAiApi() {
        OpenAiApi.Builder builder = OpenAiApi.builder()
                .baseUrl("https://openrouter.ai/api/v1")
                .apiKey("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");

        OpenAiApi openAiApi = builder.build();
        return openAiApi;
    }

    /**
     * 创建OpenAiChatModel Bean，用于执行聊天模型相关的操作
     * 
     * 该Bean依赖于openAiApi Bean，并仅在满足OpenAiApiCondition条件时创建。
     * OpenAiChatModel封装了与OpenAI聊天模型交互的高级功能。
     * 
     * @param openAiApi OpenAiApi实例，用于底层API通信
     * @return OpenAiChatModel实例
     */
    @Bean
    @Conditional(OpenAiApiCondition.class)
    public OpenAiChatModel openAiChatModel(OpenAiApi openAiApi) {
        OpenAiChatModel openAiChatModel = OpenAiChatModel.builder()
                .openAiApi(openAiApi)
                .defaultOptions(OpenAiChatOptions.builder()
                        .model("gpt-3.5-turbo")
                        .build())
                .build();
        return openAiChatModel;
    }

    @Bean
    @Conditional(com.example.config.OpenAiApiCondition.class)
    public ChatClient chatClient(OpenAiChatModel openAiChatModel) {
        return ChatClient.builder(openAiChatModel).build();
    }
}