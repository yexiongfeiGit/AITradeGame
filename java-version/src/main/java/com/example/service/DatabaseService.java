package com.example.service;

import com.example.entity.*;
import com.example.repository.*;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.data.domain.PageRequest;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;

@Service
public class DatabaseService {
    
    @Autowired
    private ProviderRepository providerRepository;
    
    @Autowired
    private ModelRepository modelRepository;
    
    @Autowired
    private PortfolioRepository portfolioRepository;
    
    @Autowired
    private TradeRepository tradeRepository;
    
    @Autowired
    private ConversationRepository conversationRepository;
    
    @Autowired
    private AccountValueRepository accountValueRepository;
    
    @Autowired
    private SettingsRepository settingsRepository;
    
    // 初始化数据库表
    public void initDb() {
        // 表结构会由JPA自动创建
    }
    
    // Provider相关方法
    public Provider saveProvider(Provider provider) {
        return providerRepository.save(provider);
    }
    
    public List<Provider> getAllProviders() {
        return providerRepository.findAll();
    }
    
    public Optional<Provider> getProviderById(Long id) {
        return providerRepository.findById(id);
    }
    
    /**
     * 创建新的提供商
     * 
     * @param provider 要创建的提供商对象
     * @return 创建的提供商ID
     */
    public Long createProvider(Provider provider) {
        Provider savedProvider = providerRepository.save(provider);
        return savedProvider.getId();
    }
    
    // Model相关方法
    public Model saveModel(Model model) {
        return modelRepository.save(model);
    }
    
    public List<Model> getAllModels() {
        return modelRepository.findAll();
    }
    
    public Optional<Model> getModelById(Long id) {
        return modelRepository.findById(id);
    }
    
    public List<Model> getModelsByProviderId(Long providerId) {
        return modelRepository.findByProviderId(providerId);
    }
    
    /**
     * 创建新的模型
     * 
     * @param model 要创建的模型对象
     * @return 创建的模型ID
     */
    public Long createModel(Model model) {
        Model savedModel = modelRepository.save(model);
        return savedModel.getId();
    }
    
    @Transactional
    public void deleteModel(Long modelId) {
        // 删除相关数据
        conversationRepository.deleteByModelId(modelId);
        accountValueRepository.deleteByModelId(modelId);
        tradeRepository.deleteByModelId(modelId);
        portfolioRepository.deleteByModelId(modelId);
        modelRepository.deleteById(modelId);
    }
    
    // Portfolio相关方法
    public Portfolio savePortfolio(Portfolio portfolio) {
        portfolio.setUpdatedAt(LocalDateTime.now());
        return portfolioRepository.save(portfolio);
    }
    
    public List<Portfolio> getPortfolioByModelId(Long modelId) {
        return portfolioRepository.findByModelId(modelId);
    }
    
    public Portfolio getPortfolioByModelIdAndCoin(Long modelId, String coin) {
        return portfolioRepository.findByModelIdAndCoin(modelId, coin);
    }
    
    public Double getTotalInvestment(Long modelId) {
        return portfolioRepository.getTotalInvestment(modelId);
    }
    
    @Transactional
    public void updatePosition(Long modelId, String coin, Double quantity, Double avgPrice, 
                              Integer leverage, String side) {
        Portfolio portfolio = portfolioRepository.findByModelIdAndCoin(modelId, coin);
        if (portfolio == null) {
            portfolio = new Portfolio(modelId, coin, quantity, avgPrice, leverage, side);
        } else {
            portfolio.setQuantity(quantity);
            portfolio.setAvgPrice(avgPrice);
            portfolio.setLeverage(leverage);
            portfolio.setSide(side);
            portfolio.setUpdatedAt(LocalDateTime.now());
        }
        portfolioRepository.save(portfolio);
    }
    
    @Transactional
    public void closePosition(Long modelId, String coin) {
        Portfolio portfolio = portfolioRepository.findByModelIdAndCoin(modelId, coin);
        if (portfolio != null) {
            portfolioRepository.delete(portfolio);
        }
    }
    
    // Trade相关方法
    public Trade saveTrade(Trade trade) {
        return tradeRepository.save(trade);
    }
    
    public List<Trade> getTradesByModelId(Long modelId) {
        return tradeRepository.findByModelIdOrderByTimestampDesc(modelId);
    }
    
    public List<Trade> getTradesByModelIdAndCoin(Long modelId, String coin) {
        return tradeRepository.findByModelIdAndCoinOrderByTimestampDesc(modelId, coin);
    }
    
    // Conversation相关方法
    public Conversation saveConversation(Conversation conversation) {
        return conversationRepository.save(conversation);
    }
    
    public List<Conversation> getConversationsByModelId(Long modelId) {
        return conversationRepository.findByModelIdOrderByTimestampDesc(modelId, PageRequest.of(0, 10));
    }
    
    // AccountValue相关方法
    public AccountValue saveAccountValue(AccountValue accountValue) {
        return accountValueRepository.save(accountValue);
    }
    
    public List<AccountValue> getAccountValuesByModelId(Long modelId) {
        return accountValueRepository.findByModelIdOrderByTimestampDesc(modelId, PageRequest.of(0, 10));
    }
    
    // Settings相关方法
    public Settings saveSetting(Settings setting) {
        return settingsRepository.save(setting);
    }
    
    public Optional<Settings> getSettingByKey(String key) {
        return settingsRepository.findByKey(key);
    }
    
    public String getSettingValue(String key, String defaultValue) {
        Optional<Settings> setting = settingsRepository.findByKey(key);
        return setting.isPresent() ? setting.get().getValue() : defaultValue;
    }
}