package com.example.config;

import org.springframework.context.annotation.Configuration;
import org.springframework.scheduling.annotation.EnableScheduling;

/**
 * 应用配置类
 * 
 * 该类是应用程序的主要配置类，用于启用和配置各种应用级功能。
 * 
 * 注解说明：
 * - @Configuration: 标记该类为Spring配置类，允许在其中定义Bean
 * - @EnableScheduling: 启用Spring的定时任务调度功能，使得@Scheduled注解生效
 */
@Configuration
@EnableScheduling
public class AppConfig {
    
}