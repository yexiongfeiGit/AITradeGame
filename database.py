"""
数据库操作模块

该模块负责处理AI炒币游戏的所有数据库操作，包括：
1. 数据库表的初始化和创建
2. API提供商信息的管理
3. 交易模型信息的管理
4. 投资组合和交易记录的管理
5. 对话历史记录的管理
6. 账户价值历史记录的管理
7. 系统设置的管理
"""

import sqlite3
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

class Database:
    """
    数据库操作类
    
    该类封装了所有与SQLite数据库交互的方法，提供了对各种业务数据的增删改查操作。
    """
    
    def __init__(self, db_path: str = 'AITradeGame.db'):
        """
        初始化数据库连接
        
        Args:
            db_path (str): 数据库文件路径，默认为'AITradeGame.db'
        """
        self.db_path = db_path
        self.conn = None
        self.connect()
    
    def connect(self):
        """
        建立数据库连接
        
        创建与SQLite数据库的连接，并设置行工厂以支持通过列名访问数据。
        """
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
    
    def init_db(self):
        """
        初始化数据库表结构
        
        创建项目所需的所有数据库表，包括：
        - providers: API提供商信息表
        - models: 交易模型信息表
        - portfolios: 投资组合信息表
        - trades: 交易记录表
        - conversations: 对话历史记录表
        - account_values: 账户价值历史记录表
        - settings: 系统设置表
        """
        cursor = self.conn.cursor()
        
        # 创建API提供商表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                api_key TEXT NOT NULL,
                api_url TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 创建交易模型表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS models (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                provider_id INTEGER,
                model_name TEXT NOT NULL,
                description TEXT,
                initial_capital REAL DEFAULT 100000,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (provider_id) REFERENCES providers (id)
            )
        ''')
        
        # 创建投资组合表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin TEXT NOT NULL,
                quantity REAL NOT NULL,
                avg_price REAL NOT NULL,
                leverage INTEGER DEFAULT 1,
                side TEXT NOT NULL,  -- long 或 short
                model_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES models (id)
            )
        ''')
        
        # 创建交易记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                coin TEXT NOT NULL,
                action TEXT NOT NULL,  -- buy, sell, close
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                leverage INTEGER DEFAULT 1,
                side TEXT NOT NULL,  -- long 或 short
                fee REAL DEFAULT 0,
                profit REAL DEFAULT 0,
                model_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES models (id)
            )
        ''')
        
        # 创建对话历史记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS conversations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER,
                prompt TEXT,
                response TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES models (id)
            )
        ''')
        
        # 创建账户价值历史记录表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS account_values (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                model_id INTEGER,
                total_value REAL NOT NULL,
                cash REAL NOT NULL,
                positions_value REAL NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (model_id) REFERENCES models (id)
            )
        ''')
        
        # 创建系统设置表
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                trading_frequency_minutes INTEGER DEFAULT 60,
                trading_fee_rate REAL DEFAULT 0.001,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # 插入默认设置（如果表为空）
        cursor.execute('SELECT COUNT(*) FROM settings')
        if cursor.fetchone()[0] == 0:
            cursor.execute('''
                INSERT INTO settings (trading_frequency_minutes, trading_fee_rate)
                VALUES (60, 0.001)
            ''')
        
        # 提交事务
        self.conn.commit()
    
    def delete_model(self, model_id: int):
        """
        删除指定的交易模型
        
        删除模型时会级联删除相关的投资组合、交易记录、对话历史和账户价值记录。
        
        Args:
            model_id (int): 要删除的模型ID
        """
        cursor = self.conn.cursor()
        
        # 删除与模型相关的所有数据
        cursor.execute('DELETE FROM account_values WHERE model_id = ?', (model_id,))
        cursor.execute('DELETE FROM conversations WHERE model_id = ?', (model_id,))
        cursor.execute('DELETE FROM trades WHERE model_id = ?', (model_id,))
        cursor.execute('DELETE FROM portfolios WHERE model_id = ?', (model_id,))
        cursor.execute('DELETE FROM models WHERE id = ?', (model_id,))
        
        # 提交事务
        self.conn.commit()
    
    def update_portfolio(self, model_id: int, coin: str, quantity: float, 
                        avg_price: float, leverage: int, side: str):
        """
        更新投资组合持仓信息
        
        Args:
            model_id (int): 模型ID
            coin (str): 币种名称
            quantity (float): 持仓数量
            avg_price (float): 平均价格
            leverage (int): 杠杆倍数
            side (str): 持仓方向（long/short）
        """
        cursor = self.conn.cursor()
        
        # 先尝试更新现有持仓
        cursor.execute('''
            UPDATE portfolios 
            SET quantity = ?, avg_price = ?, leverage = ?, side = ?, updated_at = CURRENT_TIMESTAMP
            WHERE model_id = ? AND coin = ? AND side = ?
        ''', (quantity, avg_price, leverage, side, model_id, coin, side))
        
        # 如果没有更新任何记录，则插入新记录
        if cursor.rowcount == 0:
            cursor.execute('''
                INSERT INTO portfolios (coin, quantity, avg_price, leverage, side, model_id)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (coin, quantity, avg_price, leverage, side, model_id))
        
        # 提交事务
        self.conn.commit()
    
    def get_portfolio(self, model_id: int = None) -> Dict:
        """
        获取投资组合信息
        
        Args:
            model_id (int, optional): 模型ID，如果为None则获取所有模型的汇总信息
            
        Returns:
            Dict: 包含投资组合信息的字典
        """
        cursor = self.conn.cursor()
        
        # 如果指定了模型ID，则获取该模型的投资组合
        if model_id is not None:
            cursor.execute('''
                SELECT coin, quantity, avg_price, leverage, side
                FROM portfolios 
                WHERE model_id = ?
            ''', (model_id,))
        else:
            # 否则获取所有模型的投资组合
            cursor.execute('''
                SELECT coin, quantity, avg_price, leverage, side
                FROM portfolios
            ''')
        
        # 获取查询结果
        rows = cursor.fetchall()
        
        # 构建持仓列表
        positions = []
        for row in rows:
            positions.append({
                'coin': row['coin'],
                'quantity': row['quantity'],
                'avg_price': row['avg_price'],
                'leverage': row['leverage'],
                'side': row['side']
            })
        
        return {
            'positions': positions
        }
    
    def close_position(self, model_id: int, coin: str, side: str):
        """
        平仓指定的持仓
        
        Args:
            model_id (int): 模型ID
            coin (str): 币种名称
            side (str): 持仓方向（long/short）
        """
        cursor = self.conn.cursor()
        
        # 删除指定的持仓记录
        cursor.execute('''
            DELETE FROM portfolios 
            WHERE model_id = ? AND coin = ? AND side = ?
        ''', (model_id, coin, side))
        
        # 提交事务
        self.conn.commit()
    
    def add_trade(self, model_id: int, coin: str, action: str, quantity: float,
                 price: float, leverage: int, side: str, fee: float = 0, profit: float = 0):
        """
        添加交易记录
        
        Args:
            model_id (int): 模型ID
            coin (str): 币种名称
            action (str): 交易动作（buy/sell/close）
            quantity (float): 交易数量
            price (float): 交易价格
            leverage (int): 杠杆倍数
            side (str): 交易方向（long/short）
            fee (float): 交易费用
            profit (float): 交易利润
        """
        cursor = self.conn.cursor()
        
        # 插入交易记录
        cursor.execute('''
            INSERT INTO trades (model_id, coin, action, quantity, price, leverage, side, fee, profit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (model_id, coin, action, quantity, price, leverage, side, fee, profit))
        
        # 提交事务
        self.conn.commit()
    
    def get_trades(self, model_id: int = None, limit: int = 50) -> List[Dict]:
        """
        获取交易历史记录
        
        Args:
            model_id (int, optional): 模型ID，如果为None则获取所有模型的交易记录
            limit (int): 返回记录数量限制
            
        Returns:
            List[Dict]: 交易记录列表
        """
        cursor = self.conn.cursor()
        
        # 根据是否指定模型ID构建查询语句
        if model_id is not None:
            cursor.execute('''
                SELECT * FROM trades 
                WHERE model_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (model_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM trades 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
        
        # 获取查询结果
        rows = cursor.fetchall()
        
        # 构建交易记录列表
        trades = []
        for row in rows:
            trades.append({
                'id': row['id'],
                'model_id': row['model_id'],
                'coin': row['coin'],
                'action': row['action'],
                'quantity': row['quantity'],
                'price': row['price'],
                'leverage': row['leverage'],
                'side': row['side'],
                'fee': row['fee'],
                'profit': row['profit'],
                'created_at': row['created_at']
            })
        
        return trades
    
    def add_conversation(self, model_id: int, prompt: str, response: str):
        """
        添加对话记录
        
        Args:
            model_id (int): 模型ID
            prompt (str): 提示词
            response (str): 模型响应
        """
        cursor = self.conn.cursor()
        
        # 插入对话记录
        cursor.execute('''
            INSERT INTO conversations (model_id, prompt, response)
            VALUES (?, ?, ?)
        ''', (model_id, prompt, response))
        
        # 提交事务
        self.conn.commit()
    
    def get_conversations(self, model_id: int = None, limit: int = 20) -> List[Dict]:
        """
        获取对话历史记录
        
        Args:
            model_id (int, optional): 模型ID，如果为None则获取所有模型的对话记录
            limit (int): 返回记录数量限制
            
        Returns:
            List[Dict]: 对话记录列表
        """
        cursor = self.conn.cursor()
        
        # 根据是否指定模型ID构建查询语句
        if model_id is not None:
            cursor.execute('''
                SELECT * FROM conversations 
                WHERE model_id = ? 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (model_id, limit))
        else:
            cursor.execute('''
                SELECT * FROM conversations 
                ORDER BY created_at DESC 
                LIMIT ?
            ''', (limit,))
        
        # 获取查询结果
        rows = cursor.fetchall()
        
        # 构建对话记录列表
        conversations = []
        for row in rows:
            conversations.append({
                'id': row['id'],
                'model_id': row['model_id'],
                'prompt': row['prompt'],
                'response': row['response'],
                'created_at': row['created_at']
            })
        
        return conversations
    
    def record_account_value(self, model_id: int, total_value: float, cash: float, 
                           positions_value: float):
        """
        记录账户价值快照
        
        Args:
            model_id (int): 模型ID
            total_value (float): 账户总价值
            cash (float): 现金余额
            positions_value (float): 持仓价值
        """
        cursor = self.conn.cursor()
        
        # 插入账户价值记录
        cursor.execute('''
            INSERT INTO account_values (model_id, total_value, cash, positions_value)
            VALUES (?, ?, ?, ?)
        ''', (model_id, total_value, cash, positions_value))
        
        # 提交事务
        self.conn.commit()
    
    def get_account_value_history(self, model_id: int, limit: int = 100) -> List[Dict]:
        """
        获取账户价值历史记录
        
        Args:
            model_id (int): 模型ID
            limit (int): 返回记录数量限制
            
        Returns:
            List[Dict]: 账户价值历史记录列表
        """
        cursor = self.conn.cursor()
        
        # 查询账户价值历史记录
        cursor.execute('''
            SELECT * FROM account_values 
            WHERE model_id = ? 
            ORDER BY created_at DESC 
            LIMIT ?
        ''', (model_id, limit))
        
        # 获取查询结果
        rows = cursor.fetchall()
        
        # 构建账户价值历史记录列表
        history = []
        for row in rows:
            history.append({
                'id': row['id'],
                'model_id': row['model_id'],
                'total_value': row['total_value'],
                'cash': row['cash'],
                'positions_value': row['positions_value'],
                'created_at': row['created_at']
            })
        
        return history
    
    def get_aggregated_account_value_history(self, days: int = 30) -> List[Dict]:
        """
        获取聚合的账户价值历史记录
        
        Args:
            days (int): 获取指定天数内的记录
            
        Returns:
            List[Dict]: 聚合的账户价值历史记录列表
        """
        cursor = self.conn.cursor()
        
        # 计算指定天数前的时间点
        since_date = datetime.now() - timedelta(days=days)
        
        # 查询聚合的账户价值历史记录
        cursor.execute('''
            SELECT 
                DATE(created_at) as date,
                SUM(total_value) as total_value,
                SUM(cash) as total_cash,
                SUM(positions_value) as total_positions_value
            FROM account_values 
            WHERE created_at >= ?
            GROUP BY DATE(created_at)
            ORDER BY date
        ''', (since_date,))
        
        # 获取查询结果
        rows = cursor.fetchall()
        
        # 构建聚合的账户价值历史记录列表
        history = []
        for row in rows:
            history.append({
                'date': row['date'],
                'total_value': row['total_value'],
                'cash': row['total_cash'],
                'positions_value': row['total_positions_value']
            })
        
        return history
    
    def get_multi_model_chart_data(self, days: int = 30) -> Dict:
        """
        获取多模型图表数据
        
        Args:
            days (int): 获取指定天数内的记录
            
        Returns:
            Dict: 多模型图表数据
        """
        cursor = self.conn.cursor()
        
        # 计算指定天数前的时间点
        since_date = datetime.now() - timedelta(days=days)
        
        # 查询各模型的账户价值历史记录
        cursor.execute('''
            SELECT 
                m.name as model_name,
                av.created_at,
                av.total_value
            FROM account_values av
            JOIN models m ON av.model_id = m.id
            WHERE av.created_at >= ?
            ORDER BY av.created_at
        ''', (since_date,))
        
        # 获取查询结果
        rows = cursor.fetchall()
        
        # 按模型分组整理数据
        model_data = {}
        for row in rows:
            model_name = row['model_name']
            if model_name not in model_data:
                model_data[model_name] = []
            model_data[model_name].append({
                'timestamp': row['created_at'],
                'value': row['total_value']
            })
        
        return model_data
    
    def get_settings(self) -> Dict:
        """
        获取系统设置
        
        Returns:
            Dict: 系统设置信息
        """
        cursor = self.conn.cursor()
        
        # 查询系统设置
        cursor.execute('SELECT * FROM settings ORDER BY id DESC LIMIT 1')
        row = cursor.fetchone()
        
        # 如果未设置记录，返回默认值
        if not row:
            return {
                'trading_frequency_minutes': 60,
                'trading_fee_rate': 0.001
            }
        
        # 返回设置信息
        return {
            'trading_frequency_minutes': row['trading_frequency_minutes'],
            'trading_fee_rate': row['trading_fee_rate']
        }
    
    def update_settings(self, settings: Dict):
        """
        更新系统设置
        
        Args:
            settings (Dict): 新的设置值
        """
        cursor = self.conn.cursor()
        
        # 更新系统设置
        cursor.execute('''
            UPDATE settings 
            SET trading_frequency_minutes = ?, trading_fee_rate = ?, updated_at = CURRENT_TIMESTAMP
        ''', (settings.get('trading_frequency_minutes', 60), 
              settings.get('trading_fee_rate', 0.001)))
        
        # 如果没有更新任何记录，则插入新记录
        if cursor.rowcount == 0:
            cursor.execute('''
                INSERT INTO settings (trading_frequency_minutes, trading_fee_rate)
                VALUES (?, ?)
            ''', (settings.get('trading_frequency_minutes', 60), 
                  settings.get('trading_fee_rate', 0.001)))
        
        # 提交事务
        self.conn.commit()
    
    def add_provider(self, name: str, api_key: str, api_url: str) -> int:
        """
        添加API提供商
        
        Args:
            name (str): 提供商名称
            api_key (str): API密钥
            api_url (str): API地址
            
        Returns:
            int: 新添加的提供商ID
        """
        cursor = self.conn.cursor()
        
        # 插入提供商信息
        cursor.execute('''
            INSERT INTO providers (name, api_key, api_url)
            VALUES (?, ?, ?)
        ''', (name, api_key, api_url))
        
        # 提交事务并返回新记录的ID
        self.conn.commit()
        return cursor.lastrowid
    
    def get_provider(self, provider_id: int) -> Optional[Dict]:
        """
        获取指定的API提供商信息
        
        Args:
            provider_id (int): 提供商ID
            
        Returns:
            Optional[Dict]: 提供商信息，如果未找到则返回None
        """
        cursor = self.conn.cursor()
        
        # 查询提供商信息
        cursor.execute('SELECT * FROM providers WHERE id = ?', (provider_id,))
        row = cursor.fetchone()
        
        # 如果未找到记录，返回None
        if not row:
            return None
        
        # 返回提供商信息
        return {
            'id': row['id'],
            'name': row['name'],
            'api_key': row['api_key'],
            'api_url': row['api_url'],
            'created_at': row['created_at']
        }
    
    def get_all_providers(self) -> List[Dict]:
        """
        获取所有API提供商信息
        
        Returns:
            List[Dict]: 所有提供商信息列表
        """
        cursor = self.conn.cursor()
        
        # 查询所有提供商信息
        cursor.execute('SELECT * FROM providers ORDER BY created_at DESC')
        rows = cursor.fetchall()
        
        # 构建提供商信息列表
        providers = []
        for row in rows:
            providers.append({
                'id': row['id'],
                'name': row['name'],
                'api_key': row['api_key'],
                'api_url': row['api_url'],
                'created_at': row['created_at']
            })
        
        return providers
    
    def delete_provider(self, provider_id: int):
        """
        删除指定的API提供商
        
        Args:
            provider_id (int): 要删除的提供商ID
        """
        cursor = self.conn.cursor()
        
        # 删除提供商信息
        cursor.execute('DELETE FROM providers WHERE id = ?', (provider_id,))
        
        # 提交事务
        self.conn.commit()
    
    def update_provider(self, provider_id: int, name: str, api_key: str, api_url: str):
        """
        更新API提供商信息
        
        Args:
            provider_id (int): 要更新的提供商ID
            name (str): 新的提供商名称
            api_key (str): 新的API密钥
            api_url (str): 新的API地址
        """
        cursor = self.conn.cursor()
        
        # 更新提供商信息
        cursor.execute('''
            UPDATE providers 
            SET name = ?, api_key = ?, api_url = ?
            WHERE id = ?
        ''', (name, api_key, api_url, provider_id))
        
        # 提交事务
        self.conn.commit()
    
    def add_model(self, name: str, provider_id: int, model_name: str, 
                 description: str = "", initial_capital: float = 100000) -> int:
        """
        添加交易模型
        
        Args:
            name (str): 模型名称
            provider_id (int): 提供商ID
            model_name (str): 模型名称（在提供商处的标识）
            description (str): 模型描述
            initial_capital (float): 初始资金
            
        Returns:
            int: 新添加的模型ID
        """
        cursor = self.conn.cursor()
        
        # 插入模型信息
        cursor.execute('''
            INSERT INTO models (name, provider_id, model_name, description, initial_capital)
            VALUES (?, ?, ?, ?, ?)
        ''', (name, provider_id, model_name, description, initial_capital))
        
        # 提交事务并返回新记录的ID
        self.conn.commit()
        return cursor.lastrowid
    
    def get_model(self, model_id: int) -> Optional[Dict]:
        """
        获取指定的交易模型信息
        
        Args:
            model_id (int): 模型ID
            
        Returns:
            Optional[Dict]: 模型信息，如果未找到则返回None
        """
        cursor = self.conn.cursor()
        
        # 查询模型信息（关联提供商信息）
        cursor.execute('''
            SELECT m.*, p.api_key, p.api_url
            FROM models m
            LEFT JOIN providers p ON m.provider_id = p.id
            WHERE m.id = ?
        ''', (model_id,))
        row = cursor.fetchone()
        
        # 如果未找到记录，返回None
        if not row:
            return None
        
        # 返回模型信息
        return {
            'id': row['id'],
            'name': row['name'],
            'provider_id': row['provider_id'],
            'model_name': row['model_name'],
            'description': row['description'],
            'initial_capital': row['initial_capital'],
            'created_at': row['created_at'],
            'api_key': row['api_key'],
            'api_url': row['api_url']
        }
    
    def get_all_models(self) -> List[Dict]:
        """
        获取所有交易模型信息
        
        Returns:
            List[Dict]: 所有模型信息列表
        """
        cursor = self.conn.cursor()
        
        # 查询所有模型信息（关联提供商信息）
        cursor.execute('''
            SELECT m.*, p.name as provider_name, p.api_key, p.api_url
            FROM models m
            LEFT JOIN providers p ON m.provider_id = p.id
            ORDER BY m.created_at DESC
        ''')
        rows = cursor.fetchall()
        
        # 构建模型信息列表
        models = []
        for row in rows:
            models.append({
                'id': row['id'],
                'name': row['name'],
                'provider_id': row['provider_id'],
                'provider_name': row['provider_name'],
                'model_name': row['model_name'],
                'description': row['description'],
                'initial_capital': row['initial_capital'],
                'created_at': row['created_at'],
                'api_key': row['api_key'],
                'api_url': row['api_url']
            })
        
        return models
    
    def get_leaderboard(self) -> List[Dict]:
        """
        获取排行榜信息
        
        Returns:
            List[Dict]: 排行榜信息列表
        """
        cursor = self.conn.cursor()
        
        # 查询最新的账户价值记录，用于计算收益率
        cursor.execute('''
            WITH latest_values AS (
                SELECT model_id, MAX(created_at) as latest_time
                FROM account_values
                GROUP BY model_id
            )
            SELECT 
                m.id,
                m.name,
                m.initial_capital,
                av.total_value,
                ((av.total_value - m.initial_capital) / m.initial_capital) * 100 as returns_percent
            FROM models m
            LEFT JOIN latest_values lv ON m.id = lv.model_id
            LEFT JOIN account_values av ON lv.model_id = av.model_id AND lv.latest_time = av.created_at
            ORDER BY returns_percent DESC
        ''')
        
        # 获取查询结果
        rows = cursor.fetchall()
        
        # 构建排行榜信息列表
        leaderboard = []
        for row in rows:
            leaderboard.append({
                'model_id': row['id'],
                'model_name': row['name'],
                'initial_capital': row['initial_capital'],
                'account_value': row['total_value'] or row['initial_capital'],
                'returns_percent': row['returns_percent'] or 0
            })
        
        return leaderboard

