package com.example.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * 交易模型实体类
 * 
 * 该实体类表示一个AI交易模型，包含模型的基本信息、关联的API提供商、
 * 模型名称以及初始资金等信息。每个模型代表一个独立的AI交易策略实例。
 */
@Entity
@Table(name = "models")
public class Model {
    /** 模型唯一标识符，主键，自动生成 */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    /** 模型显示名称，不能为空 */
    @Column(nullable = false)
    private String name;
    
    /** 关联的API提供商ID，用于确定使用哪个API提供商的服务 */
    @Column(name = "provider_id")
    private Long providerId;
    
    /** 实际使用的AI模型名称（如"gpt-4"），不能为空 */
    @Column(name = "model_name", nullable = false)
    private String modelName;
    
    /** 初始资金，默认为10000.0 */
    @Column(name = "initial_capital")
    private Double initialCapital = 10000.0;
    
    /** 模型创建时间 */
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    // Constructors
    public Model() {}
    
    /**
     * 构造函数
     * 
     * @param name 模型显示名称
     * @param providerId 关联的API提供商ID
     * @param modelName 实际使用的AI模型名称
     * @param initialCapital 初始资金
     */
    public Model(String name, Long providerId, String modelName, Double initialCapital) {
        this.name = name;
        this.providerId = providerId;
        this.modelName = modelName;
        this.initialCapital = initialCapital;
        this.createdAt = LocalDateTime.now();
    }
    
    // Getters and Setters
    /**
     * 获取模型ID
     * @return 模型唯一标识符
     */
    public Long getId() {
        return id;
    }
    
    /**
     * 设置模型ID
     * @param id 模型唯一标识符
     */
    public void setId(Long id) {
        this.id = id;
    }
    
    /**
     * 获取模型显示名称
     * @return 模型名称
     */
    public String getName() {
        return name;
    }
    
    /**
     * 设置模型显示名称
     * @param name 模型名称
     */
    public void setName(String name) {
        this.name = name;
    }
    
    /**
     * 获取关联的API提供商ID
     * @return API提供商ID
     */
    public Long getProviderId() {
        return providerId;
    }
    
    /**
     * 设置关联的API提供商ID
     * @param providerId API提供商ID
     */
    public void setProviderId(Long providerId) {
        this.providerId = providerId;
    }
    
    /**
     * 获取实际使用的AI模型名称
     * @return AI模型名称
     */
    public String getModelName() {
        return modelName;
    }
    
    /**
     * 设置实际使用的AI模型名称
     * @param modelName AI模型名称
     */
    public void setModelName(String modelName) {
        this.modelName = modelName;
    }
    
    /**
     * 获取初始资金
     * @return 初始资金金额
     */
    public Double getInitialCapital() {
        return initialCapital;
    }
    
    /**
     * 设置初始资金
     * @param initialCapital 初始资金金额
     */
    public void setInitialCapital(Double initialCapital) {
        this.initialCapital = initialCapital;
    }
    
    /**
     * 获取模型创建时间
     * @return 创建时间
     */
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    
    /**
     * 设置模型创建时间
     * @param createdAt 创建时间
     */
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}