package com.example.service;

import com.example.entity.Model;
import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.ai.chat.client.ChatClient;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.util.HashMap;
import java.util.Map;

@Service
public class AITraderService {
    
    private static final Logger logger = LoggerFactory.getLogger(AITraderService.class);
    
    private final ChatClient chatClient;
    private final ObjectMapper objectMapper = new ObjectMapper();
    private final boolean hasApiKey;
    
    public AITraderService() {
        this.chatClient = null;
        this.hasApiKey = false;
    }
    
    @Autowired(required = false)
    public void setChatClient(ChatClient chatClient) {
        // 通过setter注入ChatClient，如果有的话
        if (chatClient != null) {
            // 使用反射来修改final字段的值
            try {
                java.lang.reflect.Field chatClientField = this.getClass().getDeclaredField("chatClient");
                chatClientField.setAccessible(true);
                chatClientField.set(this, chatClient);
                
                java.lang.reflect.Field hasApiKeyField = this.getClass().getDeclaredField("hasApiKey");
                hasApiKeyField.setAccessible(true);
                hasApiKeyField.set(this, true);
            } catch (Exception e) {
                logger.error("Error setting chatClient via reflection: ", e);
            }
        }
    }
    
    /**
     * 做出交易决策
     */
    public Map<String, Object> makeDecision(Model model, Map<String, Object> marketState, 
                                          Map<String, Object> portfolioInfo, Map<String, Object> accountInfo) {
        try {
            // 构建提示词
            String prompt = buildPrompt(marketState, accountInfo, portfolioInfo);
            
            // 调用LLM
            String response = callLLM(prompt);
            
            // 解析响应
            return parseResponse(response);
        } catch (Exception e) {
            logger.error("Error making trading decision: {}", e.getMessage(), e);
            return new HashMap<>();
        }
    }
    
    /**
     * 构建提示词
     */
    private String buildPrompt(Map<String, Object> marketState, Map<String, Object> accountInfo, 
                              Map<String, Object> portfolioInfo) {
        StringBuilder prompt = new StringBuilder();
        prompt.append("你是一个专业的加密货币交易员，基于给定的市场数据和账户状态做出交易决策。\n\n");
        
        // 添加交易规则
        prompt.append("交易规则:\n");
        prompt.append("- 可用保证金率必须大于等于10%\n");
        prompt.append("- 单次交易金额不能超过总资金的50%\n");
        prompt.append("- 杠杆倍数最高为5倍\n");
        prompt.append("- 持仓总数量不能超过10个币种\n");
        prompt.append("- 交易信号只能是: buy, sell, close, hold\n");
        prompt.append("- 交易理由必须充分，基于技术分析和风险控制\n\n");
        
        // 添加市场状态
        prompt.append("市场状态:\n");
        prompt.append(objectMapper.valueToTree(marketState).toPrettyString()).append("\n\n");
        
        // 添加账户信息
        prompt.append("账户信息:\n");
        prompt.append(objectMapper.valueToTree(accountInfo).toPrettyString()).append("\n\n");
        
        // 添加当前持仓
        prompt.append("当前持仓:\n");
        prompt.append(objectMapper.valueToTree(portfolioInfo).toPrettyString()).append("\n\n");
        
        // 添加输出格式要求
        prompt.append("请严格按照以下JSON格式输出你的交易决策:\n");
        prompt.append("{\n");
        prompt.append("  \"signal\": \"交易信号 (buy/sell/close/hold)\",\n");
        prompt.append("  \"coin\": \"交易币种\",\n");
        prompt.append("  \"percentage\": \"交易百分比 (0-100)\",\n");
        prompt.append("  \"leverage\": \"杠杆倍数 (1-5)\",\n");
        prompt.append("  \"reason\": \"交易理由\"\n");
        prompt.append("}\n\n");
        prompt.append("如果不需要交易，请返回 {\"signal\": \"hold\", \"coin\": \"\", \"percentage\": 0, \"leverage\": 1, \"reason\": \"无需操作\"}");
        
        return prompt.toString();
    }
    
    /**
     * 调用LLM API
     */
    private String callLLM(String prompt) {
        // 如果没有API密钥，则返回模拟响应
        if (!hasApiKey) {
            logger.warn("No API key configured, returning mock response");
            return getMockDecision();
        }
        
        try {
            logger.info("Calling LLM with prompt: {}", prompt);
            String response = chatClient.prompt(prompt).call().content();
            logger.info("LLM Response: {}", response);
            return response;
        } catch (Exception e) {
            logger.error("Error calling LLM: ", e);
            // 即使API调用失败，也返回模拟响应而不是抛出异常
            logger.warn("Returning mock response due to API error");
            return getMockDecision();
        }
    }
    
    /**
     * 获取模拟决策（用于没有API密钥的情况）
     */
    private String getMockDecision() {
        // 返回一个模拟的决策响应
        return "{\n" +
                "  \"signal\": \"hold\",\n" +
                "  \"coin\": \"\",\n" +
                "  \"percentage\": 0,\n" +
                "  \"leverage\": 1,\n" +
                "  \"reason\": \"模拟决策：暂无操作\"\n" +
                "}";
    }
    
    /**
     * 解析LLM响应
     */
    private Map<String, Object> parseResponse(String response) {
        Map<String, Object> decision = new HashMap<>();
        
        try {
            // 尝试解析JSON响应
            JsonNode jsonNode = objectMapper.readTree(response);
            
            decision.put("signal", jsonNode.has("signal") ? jsonNode.get("signal").asText() : "hold");
            decision.put("coin", jsonNode.has("coin") ? jsonNode.get("coin").asText() : "");
            decision.put("percentage", jsonNode.has("percentage") ? jsonNode.get("percentage").asDouble() : 0.0);
            decision.put("leverage", jsonNode.has("leverage") ? jsonNode.get("leverage").asInt() : 1);
            decision.put("reason", jsonNode.has("reason") ? jsonNode.get("reason").asText() : "");
        } catch (Exception e) {
            logger.error("Error parsing LLM response: {}", e.getMessage());
            // 如果解析失败，返回默认持有决策
            decision.put("signal", "hold");
            decision.put("coin", "");
            decision.put("percentage", 0.0);
            decision.put("leverage", 1);
            decision.put("reason", "无法解析AI响应");
        }
        
        return decision;
    }
}