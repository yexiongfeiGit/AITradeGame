package com.example.service;

import com.example.entity.*;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.stereotype.Service;

import java.time.LocalDateTime;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;

/**
 * 交易引擎服务类
 * 
 * 该服务类负责执行AI交易模型的交易周期，包括：
 * 1. 获取市场状态和账户信息
 * 2. 调用AI模型做出交易决策
 * 3. 执行交易决策（买入、卖出、平仓等）
 * 4. 更新账户和持仓信息
 * 
 * 该类是整个AI交易系统的核心组件，协调各个服务组件完成交易流程。
 */
@Service
public class TradingEngineService {
    
    private static final Logger logger = LoggerFactory.getLogger(TradingEngineService.class);
    
    /** 数据库服务，用于访问和操作数据库中的实体数据 */
    @Autowired
    private DatabaseService databaseService;
    
    /** 市场数据服务，用于获取实时市场数据和技术指标 */
    @Autowired
    private MarketDataService marketDataService;
    
    /** AI交易服务，用于调用AI模型做出交易决策 */
    @Autowired
    private AITraderService aiTraderService;
    
    // 交易对配置
    private static final List<String> SUPPORTED_COINS = Arrays.asList(
        "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT", 
        "AVAX", "LINK", "MATIC", "UNI", "LTC", "ATOM", "ETC"
    );
    
    // 缓存市场数据
    private final Map<String, Map<String, Object>> marketDataCache = new ConcurrentHashMap<>();
    
    /**
     * 执行交易周期
     * 
     * 这是交易引擎的核心方法，负责完成一个完整的交易周期：
     * 1. 获取模型信息
     * 2. 获取市场状态
     * 3. 构建账户和投资组合信息
     * 4. 调用AI模型做出决策
     * 5. 执行交易决策
     * 6. 记录交易日志
     * 
     * @param modelId 交易模型的唯一标识符
     */
    public void executeTradingCycle(Long modelId) {
        try {
            logger.info("Starting trading cycle for model ID: {}", modelId);
            
            // 获取模型信息
            Optional<Model> modelOpt = databaseService.getModelById(modelId);
            if (!modelOpt.isPresent()) {
                logger.error("Model not found: {}", modelId);
                return;
            }
            
            Model model = modelOpt.get();
            
            // 获取市场状态
            Map<String, Object> marketState = getMarketState();
            
            // 构建账户信息
            Map<String, Object> accountInfo = buildAccountInfo(modelId, model);
            
            // 构建投资组合信息
            Map<String, Object> portfolioInfo = buildPortfolioInfo(modelId);
            
            // 格式化提示信息
            String prompt = formatPrompt(marketState, accountInfo, portfolioInfo);
            
            // 记录对话历史
            Conversation conversation = new Conversation(modelId, prompt, "");
            databaseService.saveConversation(conversation);
            
            // AI做出交易决策
            Map<String, Object> decision = aiTraderService.makeDecision(model, marketState, portfolioInfo, accountInfo);
            
            // 更新对话历史
            String decisionStr = decision.toString();
            conversation.setResponse(decisionStr);
            databaseService.saveConversation(conversation);
            
            // 执行交易决策
            executeDecisions(modelId, decision);
            
            logger.info("Trading cycle completed for model ID: {}", modelId);
        } catch (Exception e) {
            logger.error("Error executing trading cycle for model ID: {}: {}", modelId, e.getMessage(), e);
        }
    }
    
    /**
     * 获取市场状态
     * 
     * 收集当前市场的各种数据，包括：
     * 1. 各支持币种的当前价格
     * 2. 各币种的市场数据（如成交量、市值等）
     * 3. 各币种的技术指标（如移动平均线、RSI等）
     * 
     * @return 包含市场价格、市场数据和技术指标的Map对象
     */
    private Map<String, Object> getMarketState() {
        Map<String, Object> marketState = new HashMap<>();
        
        try {
            // 获取当前价格
            Map<String, Double> prices = marketDataService.getCurrentPrices(SUPPORTED_COINS.toArray(new String[0]));
            marketState.put("prices", prices);
            
            // 获取各币种的市场数据和技术指标
            Map<String, Object> coinData = new HashMap<>();
            for (String coin : SUPPORTED_COINS) {
                Map<String, Object> data = new HashMap<>();
                
                // 获取市场数据
                Map<String, Object> marketData = marketDataService.getMarketData(coin);
                data.put("market_data", marketData);
                
                // 计算技术指标
                Map<String, Object> indicators = marketDataService.calculateTechnicalIndicators(coin);
                data.put("indicators", indicators);
                
                coinData.put(coin, data);
            }
            
            marketState.put("coin_data", coinData);
        } catch (Exception e) {
            logger.error("Error getting market state: {}", e.getMessage(), e);
        }
        
        return marketState;
    }
    
    /**
     * 构建账户信息
     * 
     * 根据模型ID和模型对象构建账户相关信息，包括：
     * 1. 初始资金
     * 2. 当前总资产价值
     * 3. 可用余额
     * 4. 持仓价值
     * 5. 已用保证金
     * 6. 可用保证金比例
     * 
     * @param modelId 交易模型的唯一标识符
     * @param model 交易模型对象
     * @return 包含账户各项信息的Map对象
     */
    private Map<String, Object> buildAccountInfo(Long modelId, Model model) {
        Map<String, Object> accountInfo = new HashMap<>();
        
        try {
            // 初始资金
            Double initialCapital = model.getInitialCapital() != null ? model.getInitialCapital() : 10000.0;
            accountInfo.put("initial_capital", initialCapital);
            
            // 获取当前投资组合
            List<Portfolio> portfolios = databaseService.getPortfolioByModelId(modelId);
            
            // 计算总持仓价值
            double totalPositionValue = 0.0;
            Map<String, Double> prices = marketDataService.getCurrentPrices(SUPPORTED_COINS.toArray(new String[0]));
            
            for (Portfolio portfolio : portfolios) {
                String coin = portfolio.getCoin();
                Double price = prices.get(coin);
                if (price != null) {
                    double positionValue = portfolio.getQuantity() * price;
                    totalPositionValue += positionValue;
                }
            }
            
            // 获取账户价值历史
            List<AccountValue> accountValues = databaseService.getAccountValuesByModelId(modelId);
            Double totalValue = !accountValues.isEmpty() ? accountValues.get(0).getTotalValue() : initialCapital;
            Double availableBalance = !accountValues.isEmpty() ? accountValues.get(0).getAvailableBalance() : initialCapital;
            
            accountInfo.put("total_value", totalValue);
            accountInfo.put("available_balance", availableBalance);
            accountInfo.put("position_value", totalPositionValue);
            accountInfo.put("used_margin", totalPositionValue);
            accountInfo.put("available_margin_ratio", availableBalance / initialCapital * 100);
        } catch (Exception e) {
            logger.error("Error building account info: {}", e.getMessage(), e);
        }
        
        return accountInfo;
    }
    
    /**
     * 构建投资组合信息
     * 
     * 根据模型ID获取该模型的投资组合信息，包括：
     * 1. 各币种的持仓详情（数量、平均价格、当前价格、杠杆、方向等）
     * 2. 各持仓的当前价值和盈亏情况
     * 3. 投资组合的总价值和持仓数量
     * 
     * @param modelId 交易模型的唯一标识符
     * @return 包含投资组合各项信息的Map对象
     */
    private Map<String, Object> buildPortfolioInfo(Long modelId) {
        Map<String, Object> portfolioInfo = new HashMap<>();
        
        try {
            List<Portfolio> portfolios = databaseService.getPortfolioByModelId(modelId);
            
            // 计算总持仓价值
            double totalPositionValue = 0.0;
            Map<String, Object> positions = new HashMap<>();
            Map<String, Double> prices = marketDataService.getCurrentPrices(SUPPORTED_COINS.toArray(new String[0]));
            
            for (Portfolio portfolio : portfolios) {
                String coin = portfolio.getCoin();
                Double price = prices.get(coin);
                
                if (price != null) {
                    Map<String, Object> positionInfo = new HashMap<>();
                    positionInfo.put("quantity", portfolio.getQuantity());
                    positionInfo.put("avg_price", portfolio.getAvgPrice());
                    positionInfo.put("current_price", price);
                    positionInfo.put("leverage", portfolio.getLeverage());
                    positionInfo.put("side", portfolio.getSide());
                    
                    double positionValue = portfolio.getQuantity() * price;
                    double pnl = (price - portfolio.getAvgPrice()) * portfolio.getQuantity();
                    positionInfo.put("value", positionValue);
                    positionInfo.put("pnl", pnl);
                    
                    positions.put(coin, positionInfo);
                    totalPositionValue += positionValue;
                }
            }
            
            portfolioInfo.put("positions", positions);
            portfolioInfo.put("total_position_value", totalPositionValue);
            portfolioInfo.put("position_count", portfolios.size());
        } catch (Exception e) {
            logger.error("Error building portfolio info: {}", e.getMessage(), e);
        }
        
        return portfolioInfo;
    }
    
    /**
     * 格式化提示信息
     * 
     * 将市场状态、账户信息和投资组合信息格式化为字符串，
     * 作为输入提供给AI模型进行决策。
     * 
     * @param marketState 市场状态信息
     * @param accountInfo 账户信息
     * @param portfolioInfo 投资组合信息
     * @return 格式化后的提示信息字符串
     */
    private String formatPrompt(Map<String, Object> marketState, Map<String, Object> accountInfo, 
                               Map<String, Object> portfolioInfo) {
        StringBuilder prompt = new StringBuilder();
        prompt.append("市场状态: ").append(marketState.toString()).append("\n");
        prompt.append("账户信息: ").append(accountInfo.toString()).append("\n");
        prompt.append("投资组合: ").append(portfolioInfo.toString()).append("\n");
        return prompt.toString();
    }
    
    /**
     * 执行交易决策
     * 
     * 根据AI模型的决策执行相应的交易操作，包括：
     * 1. 买入操作
     * 2. 卖出操作
     * 3. 平仓操作
     * 4. 持仓操作
     * 
     * @param modelId 交易模型的唯一标识符
     * @param decision AI模型做出的交易决策
     */
    private void executeDecisions(Long modelId, Map<String, Object> decision) {
        try {
            String signal = (String) decision.getOrDefault("signal", "hold");
            
            switch (signal.toLowerCase()) {
                case "buy":
                    executeBuy(modelId, decision);
                    break;
                case "sell":
                    executeSell(modelId, decision);
                    break;
                case "close":
                    executeClose(modelId, decision);
                    break;
                case "hold":
                default:
                    logger.info("Holding position for model ID: {}", modelId);
                    break;
            }
        } catch (Exception e) {
            logger.error("Error executing decision for model ID: {}: {}", modelId, e.getMessage(), e);
        }
    }
    
    /**
     * 执行买入操作
     * 
     * 根据AI模型的买入决策执行具体的买入操作，包括：
     * 1. 计算买入数量和金额
     * 2. 计算手续费
     * 3. 更新账户余额
     * 4. 更新或创建持仓
     * 5. 记录交易日志
     * 6. 更新账户价值
     * 
     * @param modelId 交易模型的唯一标识符
     * @param decision AI模型做出的买入决策
     */
    private void executeBuy(Long modelId, Map<String, Object> decision) {
        try {
            String coin = (String) decision.get("coin");
            Double percentage = (Double) decision.get("percentage");
            Integer leverage = (Integer) decision.get("leverage");
            String reason = (String) decision.get("reason");
            
            if (coin == null || coin.isEmpty() || percentage == null || percentage <= 0) {
                logger.warn("Invalid buy decision for model ID: {}", modelId);
                return;
            }
            
            // 获取当前价格
            Map<String, Double> prices = marketDataService.getCurrentPrices(new String[]{coin});
            Double price = prices.get(coin);
            
            if (price == null) {
                logger.error("Failed to get price for coin: {}", coin);
                return;
            }
            
            // 获取账户信息
            List<AccountValue> accountValues = databaseService.getAccountValuesByModelId(modelId);
            if (accountValues.isEmpty()) {
                logger.error("No account value found for model ID: {}", modelId);
                return;
            }
            
            AccountValue accountValue = accountValues.get(0);
            Double availableBalance = accountValue.getAvailableBalance();
            
            // 计算交易金额
            double tradeAmount = availableBalance * (percentage / 100.0);
            double quantity = tradeAmount / price;
            
            // 计算手续费 (0.1%)
            double fee = tradeAmount * 0.001;
            
            // 更新账户余额
            double newAvailableBalance = availableBalance - tradeAmount - fee;
            
            // 更新持仓
            Portfolio existingPortfolio = databaseService.getPortfolioByModelIdAndCoin(modelId, coin);
            double newQuantity = quantity;
            double newAvgPrice = price;
            
            if (existingPortfolio != null) {
                // 加仓
                double existingQuantity = existingPortfolio.getQuantity();
                double existingAvgPrice = existingPortfolio.getAvgPrice();
                newQuantity = existingQuantity + quantity;
                newAvgPrice = (existingQuantity * existingAvgPrice + quantity * price) / newQuantity;
            }
            
            // 保存持仓
            databaseService.updatePosition(modelId, coin, newQuantity, newAvgPrice, leverage, "long");
            
            // 记录交易
            Trade trade = new Trade(modelId, coin, "buy", quantity, price, leverage, "long", 0.0, fee);
            databaseService.saveTrade(trade);
            
            // 更新账户价值
            AccountValue newAccountValue = new AccountValue(modelId, 
                accountValue.getTotalValue() - tradeAmount - fee, newAvailableBalance);
            databaseService.saveAccountValue(newAccountValue);
            
            logger.info("Executed buy order for model ID: {}, coin: {}, quantity: {}, price: {}", 
                       modelId, coin, quantity, price);
        } catch (Exception e) {
            logger.error("Error executing buy order for model ID: {}: {}", modelId, e.getMessage(), e);
        }
    }
    
    /**
     * 执行卖出操作
     * 
     * 根据AI模型的卖出决策执行具体的卖出操作，包括：
     * 1. 计算卖出数量和金额
     * 2. 计算手续费
     * 3. 计算盈亏
     * 4. 更新账户余额
     * 5. 更新或删除持仓
     * 6. 记录交易日志
     * 7. 更新账户价值
     * 
     * @param modelId 交易模型的唯一标识符
     * @param decision AI模型做出的卖出决策
     */
    private void executeSell(Long modelId, Map<String, Object> decision) {
        try {
            String coin = (String) decision.get("coin");
            Double percentage = (Double) decision.get("percentage");
            Integer leverage = (Integer) decision.get("leverage");
            String reason = (String) decision.get("reason");
            
            if (coin == null || coin.isEmpty() || percentage == null || percentage <= 0) {
                logger.warn("Invalid sell decision for model ID: {}", modelId);
                return;
            }
            
            // 获取当前价格
            Map<String, Double> prices = marketDataService.getCurrentPrices(new String[]{coin});
            Double price = prices.get(coin);
            
            if (price == null) {
                logger.error("Failed to get price for coin: {}", coin);
                return;
            }
            
            // 获取现有持仓
            Portfolio existingPortfolio = databaseService.getPortfolioByModelIdAndCoin(modelId, coin);
            if (existingPortfolio == null) {
                logger.warn("No existing position for coin: {} in model ID: {}", coin, modelId);
                return;
            }
            
            // 计算卖出数量
            double existingQuantity = existingPortfolio.getQuantity();
            double sellQuantity = existingQuantity * (percentage / 100.0);
            
            // 计算交易金额
            double tradeAmount = sellQuantity * price;
            
            // 计算手续费 (0.1%)
            double fee = tradeAmount * 0.001;
            
            // 计算盈亏
            double pnl = (price - existingPortfolio.getAvgPrice()) * sellQuantity;
            
            // 获取账户信息
            List<AccountValue> accountValues = databaseService.getAccountValuesByModelId(modelId);
            if (accountValues.isEmpty()) {
                logger.error("No account value found for model ID: {}", modelId);
                return;
            }
            
            AccountValue accountValue = accountValues.get(0);
            Double availableBalance = accountValue.getAvailableBalance();
            
            // 更新账户余额
            double newAvailableBalance = availableBalance + tradeAmount - fee;
            
            // 更新持仓
            double newQuantity = existingQuantity - sellQuantity;
            if (newQuantity <= 0.0001) {
                // 完全平仓
                databaseService.closePosition(modelId, coin);
            } else {
                // 部分平仓
                databaseService.updatePosition(modelId, coin, newQuantity, existingPortfolio.getAvgPrice(), 
                                             leverage, existingPortfolio.getSide());
            }
            
            // 记录交易
            Trade trade = new Trade(modelId, coin, "sell", sellQuantity, price, leverage, "long", pnl, fee);
            databaseService.saveTrade(trade);
            
            // 更新账户价值
            AccountValue newAccountValue = new AccountValue(modelId, 
                accountValue.getTotalValue() + tradeAmount - fee, newAvailableBalance);
            databaseService.saveAccountValue(newAccountValue);
            
            logger.info("Executed sell order for model ID: {}, coin: {}, quantity: {}, price: {}, pnl: {}", 
                       modelId, coin, sellQuantity, price, pnl);
        } catch (Exception e) {
            logger.error("Error executing sell order for model ID: {}: {}", modelId, e.getMessage(), e);
        }
    }
    
    /**
     * 执行平仓操作
     * 
     * 根据AI模型的平仓决策执行具体的平仓操作，包括：
     * 1. 计算平仓数量和金额
     * 2. 计算手续费
     * 3. 计算盈亏
     * 4. 更新账户余额
     * 5. 删除持仓
     * 6. 记录交易日志
     * 7. 更新账户价值
     * 
     * @param modelId 交易模型的唯一标识符
     * @param decision AI模型做出的平仓决策
     */
    private void executeClose(Long modelId, Map<String, Object> decision) {
        try {
            String coin = (String) decision.get("coin");
            String reason = (String) decision.get("reason");
            
            if (coin == null || coin.isEmpty()) {
                logger.warn("Invalid close decision for model ID: {}", modelId);
                return;
            }
            
            // 获取现有持仓
            Portfolio existingPortfolio = databaseService.getPortfolioByModelIdAndCoin(modelId, coin);
            if (existingPortfolio == null) {
                logger.warn("No existing position for coin: {} in model ID: {}", coin, modelId);
                return;
            }
            
            // 获取当前价格
            Map<String, Double> prices = marketDataService.getCurrentPrices(new String[]{coin});
            Double price = prices.get(coin);
            
            if (price == null) {
                logger.error("Failed to get price for coin: {}", coin);
                return;
            }
            
            // 计算交易数量和金额
            double quantity = existingPortfolio.getQuantity();
            double tradeAmount = quantity * price;
            
            // 计算手续费 (0.1%)
            double fee = tradeAmount * 0.001;
            
            // 计算盈亏
            double pnl = (price - existingPortfolio.getAvgPrice()) * quantity;
            
            // 获取账户信息
            List<AccountValue> accountValues = databaseService.getAccountValuesByModelId(modelId);
            if (accountValues.isEmpty()) {
                logger.error("No account value found for model ID: {}", modelId);
                return;
            }
            
            AccountValue accountValue = accountValues.get(0);
            Double availableBalance = accountValue.getAvailableBalance();
            
            // 更新账户余额
            double newAvailableBalance = availableBalance + tradeAmount - fee;
            
            // 删除持仓
            databaseService.closePosition(modelId, coin);
            
            // 记录交易
            Trade trade = new Trade(modelId, coin, "close", quantity, price, existingPortfolio.getLeverage(), 
                                  existingPortfolio.getSide(), pnl, fee);
            databaseService.saveTrade(trade);
            
            // 更新账户价值
            AccountValue newAccountValue = new AccountValue(modelId, 
                accountValue.getTotalValue() + tradeAmount - fee, newAvailableBalance);
            databaseService.saveAccountValue(newAccountValue);
            
            logger.info("Executed close order for model ID: {}, coin: {}, quantity: {}, price: {}, pnl: {}", 
                       modelId, coin, quantity, price, pnl);
        } catch (Exception e) {
            logger.error("Error executing close order for model ID: {}: {}", modelId, e.getMessage(), e);
        }
    }
}