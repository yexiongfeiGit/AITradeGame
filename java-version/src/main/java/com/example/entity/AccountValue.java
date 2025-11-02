package com.example.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * 账户价值实体类
 * 
 * 该实体类用于记录交易模型的账户价值变化，包括总价值和可用余额。
 * 通过时间戳可以追踪账户价值随时间的变化情况。
 */
@Entity
@Table(name = "account_values")
public class AccountValue {
    /** 账户价值记录唯一标识符，主键，自动生成 */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    /** 关联的模型ID */
    @Column(name = "model_id")
    private Long modelId;
    
    /** 账户总价值 */
    @Column(name = "total_value")
    private Double totalValue;
    
    /** 账户可用余额 */
    @Column(name = "available_balance")
    private Double availableBalance;
    
    /** 记录时间戳 */
    private LocalDateTime timestamp;
    
    // Constructors
    public AccountValue() {}
    
    /**
     * 构造函数
     * 
     * @param modelId 关联的模型ID
     * @param totalValue 账户总价值
     * @param availableBalance 账户可用余额
     */
    public AccountValue(Long modelId, Double totalValue, Double availableBalance) {
        this.modelId = modelId;
        this.totalValue = totalValue;
        this.availableBalance = availableBalance;
        this.timestamp = LocalDateTime.now();
    }
    
    // Getters and Setters
    /**
     * 获取账户价值记录ID
     * @return 账户价值记录唯一标识符
     */
    public Long getId() {
        return id;
    }
    
    /**
     * 设置账户价值记录ID
     * @param id 账户价值记录唯一标识符
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
     * 获取账户总价值
     * @return 账户总价值
     */
    public Double getTotalValue() {
        return totalValue;
    }
    
    /**
     * 设置账户总价值
     * @param totalValue 账户总价值
     */
    public void setTotalValue(Double totalValue) {
        this.totalValue = totalValue;
    }
    
    /**
     * 获取账户可用余额
     * @return 账户可用余额
     */
    public Double getAvailableBalance() {
        return availableBalance;
    }
    
    /**
     * 设置账户可用余额
     * @param availableBalance 账户可用余额
     */
    public void setAvailableBalance(Double availableBalance) {
        this.availableBalance = availableBalance;
    }
    
    /**
     * 获取记录时间戳
     * @return 记录时间
     */
    public LocalDateTime getTimestamp() {
        return timestamp;
    }
    
    /**
     * 设置记录时间戳
     * @param timestamp 记录时间
     */
    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }
}