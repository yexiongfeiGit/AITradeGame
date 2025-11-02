package com.example.entity;

import jakarta.persistence.*;

/**
 * 系统设置实体类
 * 
 * 该实体类用于存储系统的各种配置参数，以键值对的形式保存。
 * 每个设置项都有唯一的键和对应的值。
 */
@Entity
@Table(name = "settings")
public class Settings {
    /** 设置项唯一标识符，主键，自动生成 */
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private Long id;
    
    /** 设置项的键名，不能为空且唯一 */
    @Column(nullable = false, unique = true)
    private String key;
    
    /** 设置项的值，不能为空 */
    @Column(nullable = false)
    private String value;
    
    // Constructors
    public Settings() {}
    
    /**
     * 构造函数
     * 
     * @param key 设置项的键名
     * @param value 设置项的值
     */
    public Settings(String key, String value) {
        this.key = key;
        this.value = value;
    }
    
    // Getters and Setters
    /**
     * 获取设置项ID
     * @return 设置项唯一标识符
     */
    public Long getId() {
        return id;
    }
    
    /**
     * 设置设置项ID
     * @param id 设置项唯一标识符
     */
    public void setId(Long id) {
        this.id = id;
    }
    
    /**
     * 获取设置项的键名
     * @return 键名
     */
    public String getKey() {
        return key;
    }
    
    /**
     * 设置设置项的键名
     * @param key 键名
     */
    public void setKey(String key) {
        this.key = key;
    }
    
    /**
     * 获取设置项的值
     * @return 值
     */
    public String getValue() {
        return value;
    }
    
    /**
     * 设置设置项的值
     * @param value 值
     */
    public void setValue(String value) {
        this.value = value;
    }
}