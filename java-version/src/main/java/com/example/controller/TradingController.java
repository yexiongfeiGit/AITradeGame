package com.example.controller;

import com.example.entity.*;
import com.example.service.DatabaseService;
import com.example.service.TradingEngineService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.*;

@RestController
@RequestMapping("/api")
public class TradingController {
    
    @Autowired
    private DatabaseService databaseService;
    
    @Autowired
    private TradingEngineService tradingEngineService;
    
    /**
     * 获取所有提供商
     */
    @GetMapping("/providers")
    public ResponseEntity<List<Provider>> getProviders() {
        List<Provider> providers = databaseService.getAllProviders();
        return ResponseEntity.ok(providers);
    }
    
    /**
     * 添加提供商
     */
    @PostMapping("/providers")
    public ResponseEntity<Provider> addProvider(@RequestBody Provider provider) {
        Provider savedProvider = databaseService.saveProvider(provider);
        return ResponseEntity.ok(savedProvider);
    }
    
    /**
     * 删除提供商
     */
    @DeleteMapping("/providers/{id}")
    public ResponseEntity<Void> deleteProvider(@PathVariable Long id) {
        // 注意：在实际应用中，删除提供商前应检查是否有相关模型
        Optional<Provider> provider = databaseService.getProviderById(id);
        if (provider.isPresent()) {
            databaseService.deleteModel(id); // 这里应该是删除提供商的逻辑
            return ResponseEntity.ok().build();
        }
        return ResponseEntity.notFound().build();
    }
    
    /**
     * 获取所有模型
     */
    @GetMapping("/models")
    public ResponseEntity<List<Model>> getModels() {
        List<Model> models = databaseService.getAllModels();
        return ResponseEntity.ok(models);
    }
    
    /**
     * 添加模型
     */
    @PostMapping("/models")
    public ResponseEntity<Model> addModel(@RequestBody Model model) {
        Model savedModel = databaseService.saveModel(model);
        return ResponseEntity.ok(savedModel);
    }
    
    /**
     * 删除模型
     */
    @DeleteMapping("/models/{id}")
    public ResponseEntity<Void> deleteModel(@PathVariable Long id) {
        Optional<Model> model = databaseService.getModelById(id);
        if (model.isPresent()) {
            databaseService.deleteModel(id);
            return ResponseEntity.ok().build();
        }
        return ResponseEntity.notFound().build();
    }
    
    /**
     * 获取投资组合
     */
    @GetMapping("/portfolio/{modelId}")
    public ResponseEntity<Map<String, Object>> getPortfolio(@PathVariable Long modelId) {
        try {
            // 获取投资组合
            List<Portfolio> portfolios = databaseService.getPortfolioByModelId(modelId);
            
            // 构建响应数据
            Map<String, Object> response = new HashMap<>();
            response.put("positions", portfolios);
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            return ResponseEntity.status(500).build();
        }
    }
    
    /**
     * 获取交易历史
     */
    @GetMapping("/trades/{modelId}")
    public ResponseEntity<List<Trade>> getTrades(@PathVariable Long modelId) {
        List<Trade> trades = databaseService.getTradesByModelId(modelId);
        return ResponseEntity.ok(trades);
    }
    
    /**
     * 获取对话历史
     */
    @GetMapping("/conversations/{modelId}")
    public ResponseEntity<List<Conversation>> getConversations(@PathVariable Long modelId) {
        List<Conversation> conversations = databaseService.getConversationsByModelId(modelId);
        return ResponseEntity.ok(conversations);
    }
    
    /**
     * 获取账户价值历史
     */
    @GetMapping("/account-values/{modelId}")
    public ResponseEntity<List<AccountValue>> getAccountValues(@PathVariable Long modelId) {
        List<AccountValue> accountValues = databaseService.getAccountValuesByModelId(modelId);
        return ResponseEntity.ok(accountValues);
    }
    
    /**
     * 执行交易周期
     */
    @PostMapping("/trade/{modelId}")
    public ResponseEntity<Map<String, Object>> executeTrade(@PathVariable Long modelId) {
        try {
            // 执行交易周期
            tradingEngineService.executeTradingCycle(modelId);
            
            Map<String, Object> response = new HashMap<>();
            response.put("status", "success");
            response.put("message", "Trading cycle executed successfully");
            
            return ResponseEntity.ok(response);
        } catch (Exception e) {
            Map<String, Object> response = new HashMap<>();
            response.put("status", "error");
            response.put("message", "Failed to execute trading cycle: " + e.getMessage());
            
            return ResponseEntity.status(500).body(response);
        }
    }
    
    /**
     * 获取系统状态
     */
    @GetMapping("/status")
    public ResponseEntity<Map<String, Object>> getStatus() {
        Map<String, Object> status = new HashMap<>();
        status.put("status", "running");
        status.put("timestamp", new Date());
        return ResponseEntity.ok(status);
    }
}