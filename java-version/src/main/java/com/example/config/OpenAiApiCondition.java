package com.example.config;

import org.springframework.context.annotation.Condition;
import org.springframework.context.annotation.ConditionContext;
import org.springframework.core.type.AnnotatedTypeMetadata;

/**
 * OpenAI API条件配置类
 * 
 * 该类实现了Spring的Condition接口，用于决定是否应该创建与OpenAI相关的Bean。
 * 只有当满足特定条件时，AI相关的Bean才会被创建和注入到Spring容器中。
 * 
 * 条件判断逻辑：
 * 1. 检查环境变量或配置文件中是否存在"openai.api.key"属性
 * 2. 确保该属性不为空
 * 3. 确保该属性不是默认的占位符值"your-openai-api-key-here"
 */
public class OpenAiApiCondition implements Condition {
    
    /**
     * 判断是否满足创建OpenAI相关Bean的条件
     * 
     * 该方法会在Spring容器启动时被调用，用于决定是否应该创建被@Conditional注解标记的Bean。
     * 
     * @param context 条件上下文，提供了访问Spring环境和Bean工厂的方法
     * @param metadata 被@Conditional注解标记的类或方法的元数据
     * @return 如果满足条件返回true，否则返回false
     */
    @Override
    public boolean matches(ConditionContext context, AnnotatedTypeMetadata metadata) {
        // 从环境中获取OpenAI API密钥配置
        String apiKey = context.getEnvironment().getProperty("openai.api.key");
        
        // 检查API密钥是否存在、不为空且不是默认占位符值
        // 只有当API密钥配置且不为默认值时才创建Bean
        return apiKey != null && !apiKey.isEmpty() && !"your-openai-api-key-here".equals(apiKey);
    }
}