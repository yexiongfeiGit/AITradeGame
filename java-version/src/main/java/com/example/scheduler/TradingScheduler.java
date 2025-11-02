package com.example.scheduler;

import com.example.entity.Model;
import com.example.service.DatabaseService;
import com.example.service.TradingEngineService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

import java.util.List;

@Component
public class TradingScheduler {
    
    private static final Logger logger = LoggerFactory.getLogger(TradingScheduler.class);
    
    @Autowired
    private DatabaseService databaseService;
    
    @Autowired
    private TradingEngineService tradingEngineService;
    
    /**
     * 定时执行交易任务，每小时执行一次
     */
    @Scheduled(cron = "0 0 * * * ?")
    public void scheduledTradingTask() {
        logger.info("Starting scheduled trading task");
        
        try {
            // 获取所有模型
            List<Model> models = databaseService.getAllModels();
            List<Long> modelIds = models.stream().map(Model::getId).toList();
            
            // 为每个模型执行交易周期
            for (Long modelId : modelIds) {
                try {
                    tradingEngineService.executeTradingCycle(modelId);
                    logger.info("Successfully executed trading cycle for model ID: {}", modelId);
                } catch (Exception e) {
                    logger.error("Error executing trading cycle for model ID: {}: {}", modelId, e.getMessage(), e);
                }
            }
            
            logger.info("Completed scheduled trading task");
        } catch (Exception e) {
            logger.error("Error in scheduled trading task: {}", e.getMessage(), e);
        }
    }
}