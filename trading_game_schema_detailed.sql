-- AITradeGame 数据库表结构定义
-- 该SQL文件定义了AI炒币游戏项目所需的全部数据库表结构及字段说明

-- 关闭外键检查（便于初始化）
SET FOREIGN_KEY_CHECKS = 0;

-- 创建数据库（如果不存在）
CREATE DATABASE IF NOT EXISTS aitrade_game CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 使用数据库
USE aitrade_game;

-- ==================== Providers 表 ====================
-- 存储API提供商信息，用于AI模型访问不同的交易平台API
CREATE TABLE IF NOT EXISTS providers (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(255) NOT NULL COMMENT '提供商名称（如：Binance、CoinGecko等）',
    api_key VARCHAR(255) NOT NULL COMMENT 'API密钥',
    api_url VARCHAR(255) NOT NULL COMMENT 'API基础URL',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间'
) COMMENT='API提供商信息表';

-- ==================== Models 表 ====================
-- 存储AI交易模型信息，每个模型可以有不同的策略和参数
CREATE TABLE IF NOT EXISTS models (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    name VARCHAR(255) NOT NULL COMMENT '模型显示名称',
    provider_id INT COMMENT '关联的API提供商ID',
    model_name VARCHAR(255) NOT NULL COMMENT '使用的AI模型名称（如：gpt-3.5-turbo）',
    description TEXT COMMENT '模型描述信息',
    initial_capital DECIMAL(15,2) DEFAULT 100000.00 COMMENT '初始资金，默认100000.00',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    FOREIGN KEY (provider_id) REFERENCES providers (id) COMMENT '外键约束：关联providers表'
) COMMENT='AI交易模型信息表';

-- ==================== Portfolios 表 ====================
-- 存储投资组合信息，记录每个模型持有的仓位
CREATE TABLE IF NOT EXISTS portfolios (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    coin VARCHAR(50) NOT NULL COMMENT '交易币种（如：BTC、ETH等）',
    quantity DECIMAL(15,8) NOT NULL COMMENT '持仓数量',
    avg_price DECIMAL(15,8) NOT NULL COMMENT '平均持仓价格',
    leverage INT DEFAULT 1 COMMENT '杠杆倍数，默认为1',
    side VARCHAR(10) NOT NULL COMMENT '持仓方向，"long"做多或"short"做空',
    model_id INT COMMENT '关联的模型ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间',
    FOREIGN KEY (model_id) REFERENCES models (id) COMMENT '外键约束：关联models表'
) COMMENT='投资组合信息表';

-- ==================== Trades 表 ====================
-- 存储交易记录，记录所有买入、卖出和平仓操作
CREATE TABLE IF NOT EXISTS trades (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    coin VARCHAR(50) NOT NULL COMMENT '交易币种（如：BTC、ETH等）',
    action VARCHAR(20) NOT NULL COMMENT '交易动作："buy"买入、"sell"卖出、"close"平仓',
    quantity DECIMAL(15,8) NOT NULL COMMENT '交易数量',
    price DECIMAL(15,8) NOT NULL COMMENT '交易价格',
    leverage INT DEFAULT 1 COMMENT '杠杆倍数，默认为1',
    side VARCHAR(10) NOT NULL COMMENT '交易方向，"long"做多或"short"做空',
    fee DECIMAL(15,8) DEFAULT 0 COMMENT '手续费',
    profit DECIMAL(15,8) DEFAULT 0 COMMENT '利润',
    model_id INT COMMENT '关联的模型ID',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '交易时间',
    FOREIGN KEY (model_id) REFERENCES models (id) COMMENT '外键约束：关联models表'
) COMMENT='交易记录表';

-- ==================== Conversations 表 ====================
-- 存储AI模型的对话历史记录，用于跟踪模型决策过程
CREATE TABLE IF NOT EXISTS conversations (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    model_id INT COMMENT '关联的模型ID',
    prompt TEXT COMMENT '用户提示词',
    response TEXT COMMENT '模型响应内容',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '对话时间',
    FOREIGN KEY (model_id) REFERENCES models (id) COMMENT '外键约束：关联models表'
) COMMENT='AI对话历史记录表';

-- ==================== Account Values 表 ====================
-- 存储账户价值历史记录，用于跟踪账户随时间的价值变化
CREATE TABLE IF NOT EXISTS account_values (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    model_id INT COMMENT '关联的模型ID',
    total_value DECIMAL(15,2) NOT NULL COMMENT '账户总价值',
    cash DECIMAL(15,2) NOT NULL COMMENT '现金余额',
    positions_value DECIMAL(15,2) NOT NULL COMMENT '持仓价值',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '记录时间',
    FOREIGN KEY (model_id) REFERENCES models (id) COMMENT '外键约束：关联models表'
) COMMENT='账户价值历史记录表';

-- ==================== Settings 表 ====================
-- 存储系统设置信息
CREATE TABLE IF NOT EXISTS settings (
    id INT PRIMARY KEY AUTO_INCREMENT COMMENT '主键ID',
    trading_frequency_minutes INT DEFAULT 60 COMMENT '交易频率（分钟），默认60分钟',
    trading_fee_rate DECIMAL(5,4) DEFAULT 0.0010 COMMENT '交易费率，默认0.0010（0.1%）',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP COMMENT '创建时间',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '更新时间'
) COMMENT='系统设置表';

-- 插入默认设置（如果表为空）
INSERT IGNORE INTO settings (trading_frequency_minutes, trading_fee_rate) VALUES (60, 0.0010);

-- 重新启用外键检查
SET FOREIGN_KEY_CHECKS = 1;

-- ==================== 索引优化建议 ====================
-- 为了提高查询性能，建议添加以下索引：

-- 为经常查询的字段添加索引
-- ALTER TABLE portfolios ADD INDEX idx_model_coin_side (model_id, coin, side);
-- ALTER TABLE trades ADD INDEX idx_model_created (model_id, created_at);
-- ALTER TABLE account_values ADD INDEX idx_model_created (model_id, created_at);
-- ALTER TABLE conversations ADD INDEX idx_model_created (model_id, created_at);