package com.example.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * 投资组合实体类
 * 
 * 该实体类表示一个交易模型的投资组合，包含持有的币种、数量、平均价格、
 * 杠杆倍数、交易方向等信息。每个模型可以持有多币种的投资组合。
 */
@Entity
@Table(name = "portfolios")
public class Portfolio {
    /** 投资组合记录唯一标识符，主键，自动生成 */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    /** 关联的模型ID */
    @Column(name = "model_id")
    private Long modelId;
    
    /** 持有的币种，不能为空 */
    @Column(nullable = false)
    private String coin;
    
    /** 持有数量，不能为空 */
    @Column(nullable = false)
    private Double quantity;
    
    /** 平均买入价格 */
    @Column(name = "avg_price")
    private Double avgPrice;
    
    /** 杠杆倍数，默认为1（无杠杆） */
    private Integer leverage = 1;
    
    /** 交易方向，默认为"long"（做多） */
    private String side = "long";
    
    /** 记录更新时间 */
    @Column(name = "updated_at")
    private LocalDateTime updatedAt;
    
    // Constructors
    public Portfolio() {}
    
    /**
     * 构造函数
     * 
     * @param modelId 关联的模型ID
     * @param coin 持有的币种
     * @param quantity 持有数量
     * @param avgPrice 平均买入价格
     * @param leverage 杠杆倍数
     * @param side 交易方向
     */
    public Portfolio(Long modelId, String coin, Double quantity, Double avgPrice, Integer leverage, String side) {
        this.modelId = modelId;
        this.coin = coin;
        this.quantity = quantity;
        this.avgPrice = avgPrice;
        this.leverage = leverage;
        this.side = side;
        this.updatedAt = LocalDateTime.now();
    }
    
    // Getters and Setters
    /**
     * 获取投资组合记录ID
     * @return 投资组合记录唯一标识符
     */
    public Long getId() {
        return id;
    }
    
    /**
     * 设置投资组合记录ID
     * @param id 投资组合记录唯一标识符
     */
    public void setId(Long id) {
        this.id = id;
    }
    
    /**
     * 获取关联的模型ID
     * @return 模型ID
     */
    public Long getModelId() {
        return modelId;
    }
    
    /**
     * 设置关联的模型ID
     * @param modelId 模型ID
     */
    public void setModelId(Long modelId) {
        this.modelId = modelId;
    }
    
    /**
     * 获取持有的币种
     * @return 币种名称
     */
    public String getCoin() {
        return coin;
    }
    
    /**
     * 设置持有的币种
     * @param coin 币种名称
     */
    public void setCoin(String coin) {
        this.coin = coin;
    }
    
    /**
     * 获取持有数量
     * @return 持有数量
     */
    public Double getQuantity() {
        return quantity;
    }
    
    /**
     * 设置持有数量
     * @param quantity 持有数量
     */
    public void setQuantity(Double quantity) {
        this.quantity = quantity;
    }
    
    /**
     * 获取平均买入价格
     * @return 平均买入价格
     */
    public Double getAvgPrice() {
        return avgPrice;
    }
    
    /**
     * 设置平均买入价格
     * @param avgPrice 平均买入价格
     */
    public void setAvgPrice(Double avgPrice) {
        this.avgPrice = avgPrice;
    }
    
    /**
     * 获取杠杆倍数
     * @return 杠杆倍数
     */
    public Integer getLeverage() {
        return leverage;
    }
    
    /**
     * 设置杠杆倍数
     * @param leverage 杠杆倍数
     */
    public void setLeverage(Integer leverage) {
        this.leverage = leverage;
    }
    
    /**
     * 获取交易方向
     * @return 交易方向（"long"或"short"）
     */
    public String getSide() {
        return side;
    }
    
    /**
     * 设置交易方向
     * @param side 交易方向（"long"或"short"）
     */
    public void setSide(String side) {
        this.side = side;
    }
    
    /**
     * 获取记录更新时间
     * @return 更新时间
     */
    public LocalDateTime getUpdatedAt() {
        return updatedAt;
    }
    
    /**
     * 设置记录更新时间
     * @param updatedAt 更新时间
     */
    public void setUpdatedAt(LocalDateTime updatedAt) {
        this.updatedAt = updatedAt;
    }
}