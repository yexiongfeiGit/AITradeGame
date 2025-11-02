package com.example;

import org.springframework.ai.model.openai.autoconfigure.OpenAiModerationAutoConfiguration;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Spring Boot应用程序的主入口类
 * 
 * 该类负责启动整个AITradeGame应用程序，使用Spring Boot框架简化配置和部署。
 * 
 * 注解说明：
 * - @SpringBootApplication: 这是一个组合注解，包含了:
 * - @Configuration: 标记该类为配置类
 * - @EnableAutoConfiguration: 启用Spring Boot的自动配置机制
 * - @ComponentScan: 启用组件扫描，自动发现和注册Spring组件
 * - exclude = {OpenAiAutoConfiguration.class}: 排除OpenAI自动配置，因为我们有自己的AI配置类
 */
@SpringBootApplication(exclude = { OpenAiModerationAutoConfiguration.class })
public class AITradeGameApplication {

    /**
     * 应用程序的主入口方法
     * 
     * SpringApplication.run()方法会:
     * 1. 创建Spring应用上下文
     * 2. 执行自动配置
     * 3. 启动嵌入式Web服务器（如果是一个Web应用）
     * 4. 初始化所有Spring Bean
     * 
     * @param args 命令行参数
     */
    public static void main(String[] args) {
        SpringApplication.run(AITradeGameApplication.class, args);
    }

}