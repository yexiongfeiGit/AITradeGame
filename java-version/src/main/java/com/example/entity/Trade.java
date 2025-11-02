package com.example.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * 交易记录实体类
 * 
 * 该实体类表示一次具体的交易操作，包含交易的币种、信号、数量、价格、
 * 杠杆倍数、交易方向、盈亏、手续费等信息。用于记录和追踪所有的交易历史。
 */
@Entity
@Table(name = "trades")
public class Trade {
    /** 交易记录唯一标识符，主键，自动生成 */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    /** 关联的模型ID */
    @Column(name = "model_id")
    private Long modelId;
    
    /** 交易的币种，不能为空 */
    @Column(nullable = false)
    private String coin;
    
    /** 交易信号（如"BUY"或"SELL"），不能为空 */
    @Column(nullable = false)
    private String signal;
    
    /** 交易数量，不能为空 */
    @Column(nullable = false)
    private Double quantity;
    
    /** 交易价格，不能为空 */
    @Column(nullable = false)
    private Double price;
    
    /** 杠杆倍数，默认为1（无杠杆） */
    private Integer leverage = 1;
    
    /** 交易方向，默认为"long"（做多） */
    private String side = "long";
    
    /** 本次交易的盈亏，默认为0.0 */
    private Double pnl = 0.0;
    
    /** 本次交易的手续费，默认为0.0 */
    private Double fee = 0.0;
    
    /** 交易时间戳 */
    private LocalDateTime timestamp;
    
    // Constructors
    public Trade() {}
    
    /**
     * 构造函数
     * 
     * @param modelId 关联的模型ID
     * @param coin 交易的币种
     * @param signal 交易信号
     * @param quantity 交易数量
     * @param price 交易价格
     * @param leverage 杠杆倍数
     * @param side 交易方向
     * @param pnl 本次交易的盈亏
     * @param fee 本次交易的手续费
     */
    public Trade(Long modelId, String coin, String signal, Double quantity, Double price, Integer leverage, String side, Double pnl, Double fee) {
        this.modelId = modelId;
        this.coin = coin;
        this.signal = signal;
        this.quantity = quantity;
        this.price = price;
        this.leverage = leverage;
        this.side = side;
        this.pnl = pnl;
        this.fee = fee;
        this.timestamp = LocalDateTime.now();
    }
    
    // Getters and Setters
    /**
     * 获取交易记录ID
     * @return 交易记录唯一标识符
     */
    public Long getId() {
        return id;
    }
    
    /**
     * 设置交易记录ID
     * @param id 交易记录唯一标识符
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
     * 获取交易的币种
     * @return 币种名称
     */
    public String getCoin() {
        return coin;
    }
    
    /**
     * 设置交易的币种
     * @param coin 币种名称
     */
    public void setCoin(String coin) {
        this.coin = coin;
    }
    
    /**
     * 获取交易信号
     * @return 交易信号（如"BUY"或"SELL"）
     */
    public String getSignal() {
        return signal;
    }
    
    /**
     * 设置交易信号
     * @param signal 交易信号（如"BUY"或"SELL"）
     */
    public void setSignal(String signal) {
        this.signal = signal;
    }
    
    /**
     * 获取交易数量
     * @return 交易数量
     */
    public Double getQuantity() {
        return quantity;
    }
    
    /**
     * 设置交易数量
     * @param quantity 交易数量
     */
    public void setQuantity(Double quantity) {
        this.quantity = quantity;
    }
    
    /**
     * 获取交易价格
     * @return 交易价格
     */
    public Double getPrice() {
        return price;
    }
    
    /**
     * 设置交易价格
     * @param price 交易价格
     */
    public void setPrice(Double price) {
        this.price = price;
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
     * 获取本次交易的盈亏
     * @return 盈亏金额
     */
    public Double getPnl() {
        return pnl;
    }
    
    /**
     * 设置本次交易的盈亏
     * @param pnl 盈亏金额
     */
    public void setPnl(Double pnl) {
        this.pnl = pnl;
    }
    
    /**
     * 获取本次交易的手续费
     * @return 手续费金额
     */
    public Double getFee() {
        return fee;
    }
    
    /**
     * 设置本次交易的手续费
     * @param fee 手续费金额
     */
    public void setFee(Double fee) {
        this.fee = fee;
    }
    
    /**
     * 获取交易时间戳
     * @return 交易时间
     */
    public LocalDateTime getTimestamp() {
        return timestamp;
    }
    
    /**
     * 设置交易时间戳
     * @param timestamp 交易时间
     */
    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }
}