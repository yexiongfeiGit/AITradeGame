package com.example.entity;

import jakarta.persistence.*;
import java.time.LocalDateTime;

/**
 * 对话记录实体类
 * 
 * 该实体类用于存储AI模型与系统之间的对话记录，包括发送给AI的提示信息
 * 和AI返回的响应内容。每条记录都关联到特定的交易模型，并记录了对话时间。
 */
@Entity
@Table(name = "conversations")
public class Conversation {
    /** 对话记录唯一标识符，主键，自动生成 */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    /** 关联的模型ID */
    @Column(name = "model_id")
    private Long modelId;
    
    /** 发送给AI的提示信息，最大长度1000字符 */
    @Column(length = 1000)
    private String prompt;
    
    /** AI返回的响应内容，最大长度1000字符 */
    @Column(length = 1000)
    private String response;
    
    /** 对话时间戳 */
    private LocalDateTime timestamp;
    
    // Constructors
    public Conversation() {}
    
    /**
     * 构造函数
     * 
     * @param modelId 关联的模型ID
     * @param prompt 发送给AI的提示信息
     * @param response AI返回的响应内容
     */
    public Conversation(Long modelId, String prompt, String response) {
        this.modelId = modelId;
        this.prompt = prompt;
        this.response = response;
        this.timestamp = LocalDateTime.now();
    }
    
    // Getters and Setters
    /**
     * 获取对话记录ID
     * @return 对话记录唯一标识符
     */
    public Long getId() {
        return id;
    }
    
    /**
     * 设置对话记录ID
     * @param id 对话记录唯一标识符
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
     * 获取发送给AI的提示信息
     * @return 提示信息
     */
    public String getPrompt() {
        return prompt;
    }
    
    /**
     * 设置发送给AI的提示信息
     * @param prompt 提示信息
     */
    public void setPrompt(String prompt) {
        this.prompt = prompt;
    }
    
    /**
     * 获取AI返回的响应内容
     * @return 响应内容
     */
    public String getResponse() {
        return response;
    }
    
    /**
     * 设置AI返回的响应内容
     * @param response 响应内容
     */
    public void setResponse(String response) {
        this.response = response;
    }
    
    /**
     * 获取对话时间戳
     * @return 对话时间
     */
    public LocalDateTime getTimestamp() {
        return timestamp;
    }
    
    /**
     * 设置对话时间戳
     * @param timestamp 对话时间
     */
    public void setTimestamp(LocalDateTime timestamp) {
        this.timestamp = timestamp;
    }
}