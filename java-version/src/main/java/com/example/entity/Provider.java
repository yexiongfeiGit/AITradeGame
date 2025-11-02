package com.example.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * API提供商实体类
 * 
 * 该实体类表示一个AI服务提供商，包含提供商的基本信息，
 * 如名称、API地址、API密钥等。系统支持多个不同的AI服务提供商，
 * 每个模型可以关联到不同的提供商。
 */
@Entity
@Table(name = "providers")
public class Provider {
    /** 提供商唯一标识符，主键，自动生成 */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    /** 提供商名称，不能为空 */
    @Column(nullable = false)
    private String name;
    
    /** API地址，不能为空 */
    @Column(name = "api_url", nullable = false)
    private String apiUrl;
    
    /** API密钥，不能为空 */
    @Column(name = "api_key", nullable = false)
    private String apiKey;
    
    /** 支持的模型列表，以逗号分隔的字符串形式存储 */
    private String models;
    
    /** 提供商创建时间 */
    @Column(name = "created_at")
    private LocalDateTime createdAt;
    
    // Constructors
    public Provider() {}
    
    /**
     * 构造函数
     * 
     * @param name 提供商名称
     * @param apiUrl API地址
     * @param apiKey API密钥
     */
    public Provider(String name, String apiUrl, String apiKey) {
        this.name = name;
        this.apiUrl = apiUrl;
        this.apiKey = apiKey;
        this.createdAt = LocalDateTime.now();
    }
    
    // Getters and Setters
    /**
     * 获取提供商ID
     * @return 提供商唯一标识符
     */
    public Long getId() {
        return id;
    }
    
    /**
     * 设置提供商ID
     * @param id 提供商唯一标识符
     */
    public void setId(Long id) {
        this.id = id;
    }
    
    /**
     * 获取提供商名称
     * @return 提供商名称
     */
    public String getName() {
        return name;
    }
    
    /**
     * 设置提供商名称
     * @param name 提供商名称
     */
    public void setName(String name) {
        this.name = name;
    }
    
    /**
     * 获取API地址
     * @return API地址
     */
    public String getApiUrl() {
        return apiUrl;
    }
    
    /**
     * 设置API地址
     * @param apiUrl API地址
     */
    public void setApiUrl(String apiUrl) {
        this.apiUrl = apiUrl;
    }
    
    /**
     * 获取API密钥
     * @return API密钥
     */
    public String getApiKey() {
        return apiKey;
    }
    
    /**
     * 设置API密钥
     * @param apiKey API密钥
     */
    public void setApiKey(String apiKey) {
        this.apiKey = apiKey;
    }
    
    /**
     * 获取支持的模型列表
     * @return 以逗号分隔的模型列表字符串
     */
    public String getModels() {
        return models;
    }
    
    /**
     * 设置支持的模型列表
     * @param models 以逗号分隔的模型列表字符串
     */
    public void setModels(String models) {
        this.models = models;
    }
    
    /**
     * 获取提供商创建时间
     * @return 创建时间
     */
    public LocalDateTime getCreatedAt() {
        return createdAt;
    }
    
    /**
     * 设置提供商创建时间
     * @param createdAt 创建时间
     */
    public void setCreatedAt(LocalDateTime createdAt) {
        this.createdAt = createdAt;
    }
}