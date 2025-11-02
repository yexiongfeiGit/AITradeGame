package com.example.config;

import com.example.entity.Model;
import com.example.entity.Provider;
import com.example.service.DatabaseService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

/**
 * 数据初始化类，用于在应用程序启动时初始化默认数据
 * 
 * 该类实现了CommandLineRunner接口，确保在Spring Boot应用程序启动后执行数据初始化逻辑。
 * 主要功能是在数据库中创建默认的提供商和模型数据，以便应用程序可以正常运行。
 */
@Component
public class DataInitializer implements CommandLineRunner {
    
    private static final Logger logger = LoggerFactory.getLogger(DataInitializer.class);
    
    /**
     * 数据库服务Bean，用于执行数据库操作
     * 
     * 通过@Autowired注解自动注入DatabaseService实例。
     */
    @Autowired
    private DatabaseService databaseService;
    
    /**
     * 在应用程序启动后执行数据初始化
     * 
     * 该方法会在Spring Boot应用程序完全启动后自动调用，用于检查和创建默认数据：
     * 1. 检查数据库中是否已存在提供商数据
     * 2. 如果不存在，则创建默认的Binance提供商
     * 3. 创建默认的GPT-3.5 Trader模型，初始资金为10000美元
     * 
     * @param args 命令行参数
     * @throws Exception 如果初始化过程中发生错误
     */
    @Override
    public void run(String... args) throws Exception {
        logger.info("Initializing default data");
        
        // 检查是否已存在提供商数据
        if (databaseService.getAllProviders().isEmpty()) {
            // 创建默认提供商 (Binance)
            Provider binance = new Provider("Binance", "https://api.binance.com", "your-binance-api-key");
            Long providerId = databaseService.createProvider(binance);
            logger.info("Created default provider: Binance with ID: {}", providerId);
            
            // 创建默认模型 (GPT-3.5)
            Model model = new Model("GPT-3.5 Trader", providerId, "gpt-3.5-turbo", 10000.0);
            Long modelId = databaseService.createModel(model);
            logger.info("Created default model: GPT-3.5 Trader with ID: {}", modelId);
        } else {
            logger.info("Providers already exist, skipping initialization");
        }
    }
}