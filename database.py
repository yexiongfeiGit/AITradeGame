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

import pymysql
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple

class Database:
    """
    数据库操作类
    
    该类封装了所有与MySQL数据库交互的方法，提供了对各种业务数据的增删改查操作。
    """
    
    def __init__(self, host: str = 'localhost', port: int = 3306, user: str = 'root', 
                 password: str = '', database: str = 'aitrade_game'):
        """
        初始化数据库连接
        
        Args:
            host (str): MySQL服务器主机地址，默认为'localhost'
            port (int): MySQL服务器端口，默认为3306
            user (str): MySQL用户名，默认为'root'
            password (str): MySQL密码，默认为空
            database (str): 数据库名称，默认为'aitrade_game'
        """
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.conn = None
        self.connect()
    
    def connect(self):
        """
        建立数据库连接
        
        创建与MySQL数据库的连接，并设置字符集以支持中文。
        """
        self.conn = pymysql.connect(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    
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
        with self.conn.cursor() as cursor:
            # 创建API提供商表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS providers (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(255) NOT NULL,
                    api_key VARCHAR(255) NOT NULL,
                    api_url VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建交易模型表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS models (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    name VARCHAR(255) NOT NULL,
                    provider_id INT,
                    model_name VARCHAR(255) NOT NULL,
                    description TEXT,
                    initial_capital DECIMAL(15,2) DEFAULT 100000.00,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (provider_id) REFERENCES providers (id)
                )
            ''')
            
            # 创建投资组合表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS portfolios (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    coin VARCHAR(50) NOT NULL,
                    quantity DECIMAL(15,8) NOT NULL,
                    avg_price DECIMAL(15,8) NOT NULL,
                    leverage INT DEFAULT 1,
                    side VARCHAR(10) NOT NULL,  -- long 或 short
                    model_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    FOREIGN KEY (model_id) REFERENCES models (id)
                )
            ''')
            
            # 创建交易记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    coin VARCHAR(50) NOT NULL,
                    action VARCHAR(20) NOT NULL,  -- buy, sell, close
                    quantity DECIMAL(15,8) NOT NULL,
                    price DECIMAL(15,8) NOT NULL,
                    leverage INT DEFAULT 1,
                    side VARCHAR(10) NOT NULL,  -- long 或 short
                    fee DECIMAL(15,8) DEFAULT 0,
                    profit DECIMAL(15,8) DEFAULT 0,
                    model_id INT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (model_id) REFERENCES models (id)
                )
            ''')
            
            # 创建对话历史记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS conversations (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    model_id INT,
                    prompt TEXT,
                    response TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (model_id) REFERENCES models (id)
                )
            ''')
            
            # 创建账户价值历史记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS account_values (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    model_id INT,
                    total_value DECIMAL(15,2) NOT NULL,
                    cash DECIMAL(15,2) NOT NULL,
                    positions_value DECIMAL(15,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (model_id) REFERENCES models (id)
                )
            ''')
            
            # 创建系统设置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    trading_frequency_minutes INT DEFAULT 60,
                    trading_fee_rate DECIMAL(5,4) DEFAULT 0.0010,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                )
            ''')
            
            # 提交事务
            self.conn.commit()
            
            # 插入默认设置（如果表为空）
            cursor.execute('SELECT COUNT(*) as count FROM settings')
            result = cursor.fetchone()
            if result['count'] == 0:
                cursor.execute('''
                    INSERT INTO settings (trading_frequency_minutes, trading_fee_rate)
                    VALUES (60, 0.0010)
                ''')
                self.conn.commit()
    
    def delete_model(self, model_id: int) -> bool:
        """
        删除AI模型配置
        
        Args:
            model_id: 要删除的模型ID
            
        Returns:
            bool: 删除成功返回True，否则返回False
        """
        with self.conn.cursor() as cursor:
            cursor.execute('DELETE FROM models WHERE id = %s', (model_id,))
            self.conn.commit()
            return cursor.rowcount > 0

    def update_model(self, model_id: int, name: str, provider_id: int, model_name: str, 
                     description: str = "") -> bool:
        """
        更新AI模型配置
        
        Args:
            model_id: 要更新的模型ID
            name: 新的模型显示名称
            provider_id: 新的API提供商ID
            model_name: 新的模型名称
            description: 新的描述信息
            
        Returns:
            bool: 更新成功返回True，否则返回False
        """
        with self.conn.cursor() as cursor:
            cursor.execute('''
                UPDATE models 
                SET name = %s, provider_id = %s, model_name = %s, description = %s
                WHERE id = %s
            ''', (name, provider_id, model_name, description, model_id))
            self.conn.commit()
            return cursor.rowcount > 0
    
    def update_portfolio(self, model_id: int, coin: str, quantity: float, avg_price: float, 
                         leverage: int = 1, side: str = "long"):
        """
        更新或插入投资组合记录
        
        Args:
            model_id: 模型ID
            coin: 交易币种
            quantity: 数量
            avg_price: 平均价格
            leverage: 杠杆倍数，默认为1
            side: 方向，"long"做多或"short"做空，默认为"long"
        """
        with self.conn.cursor() as cursor:
            # 先尝试更新现有记录
            cursor.execute('''
                UPDATE portfolios 
                SET quantity = %s, avg_price = %s, leverage = %s, side = %s, updated_at = CURRENT_TIMESTAMP
                WHERE model_id = %s AND coin = %s AND side = %s
            ''', (quantity, avg_price, leverage, side, model_id, coin, side))
            
            # 如果没有更新任何记录，则插入新记录
            if cursor.rowcount == 0:
                cursor.execute('''
                    INSERT INTO portfolios (coin, quantity, avg_price, leverage, side, model_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                ''', (coin, quantity, avg_price, leverage, side, model_id))
            
            self.conn.commit()
    
    def get_portfolio(self, model_id: int = None) -> Dict:
        """
        获取投资组合信息
        
        Args:
            model_id: 模型ID，如果为None则获取所有模型的投资组合
            
        Returns:
            dict: 投资组合信息字典
        """
        with self.conn.cursor() as cursor:
            if model_id is not None:
                cursor.execute('''
                    SELECT coin, quantity, avg_price, leverage, side, model_id, created_at, updated_at
                    FROM portfolios 
                    WHERE coin = %s
                ''', (model_id,))
            else:
                cursor.execute('''
                    SELECT coin, quantity, avg_price, leverage, side, model_id, created_at, updated_at
                    FROM portfolios
                ''')
            
            rows = cursor.fetchall()
            print(f"rows: {rows}")
            portfolio = {}
            for row in rows:
                coin = row[0]
                if coin not in portfolio:
                    portfolio[coin] = []
                portfolio[coin].append({
                    'quantity': float(row[1]),
                    'avg_price': float(row[2]),
                    'leverage': row[3],
                    'side': row[4],
                    'model_id': row[5],
                    'created_at': row[6],
                    'updated_at': row[7]
                })
            
            return portfolio
    
    def close_position(self, model_id: int, coin: str, side: str):
        """
        平仓操作，删除指定的投资组合记录
        
        Args:
            model_id: 模型ID
            coin: 交易币种
            side: 持仓方向（long/short）
        """
        with self.conn.cursor() as cursor:
            cursor.execute('''
                DELETE FROM portfolios 
                WHERE model_id = %s AND coin = %s AND side = %s
            ''', (model_id, coin, side))
            self.conn.commit()
    
    def add_trade(self, model_id: int, coin: str, action: str, quantity: float,
                 price: float, leverage: int = 1, side: str = "long",
                 fee: float = 0, profit: float = 0):
        """
        添加交易记录
        
        Args:
            model_id: 模型ID
            coin: 交易币种
            action: 交易动作（buy/sell/close）
            quantity: 数量
            price: 价格
            leverage: 杠杆倍数，默认为1
            side: 方向，"long"做多或"short"做空，默认为"long"
            fee: 手续费，默认为0
            profit: 利润，默认为0
        """
        with self.conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO trades (coin, action, quantity, price, leverage, side, fee, profit, model_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ''', (coin, action, quantity, price, leverage, side, fee, profit, model_id))
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
        with self.conn.cursor() as cursor:
            # 根据是否指定模型ID构建查询语句
            if model_id is not None:
                cursor.execute('''
                    SELECT id, coin, action, quantity, price, leverage, side, fee, profit, model_id, created_at
                    FROM trades 
                    WHERE model_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT %s
                ''', (model_id, limit))
            else:
                cursor.execute('''
                    SELECT id, coin, action, quantity, price, leverage, side, fee, profit, model_id, created_at
                    FROM trades 
                    ORDER BY created_at DESC 
                    LIMIT %s
                ''', (limit,))
            
            # 获取查询结果
            rows = cursor.fetchall()
            
            # 构建交易记录列表
            trades = []
            for row in rows:
                trades.append({
                    'id': row[0],
                    'model_id': row[9],
                    'coin': row[1],
                    'action': row[2],
                    'quantity': float(row[3]),
                    'price': float(row[4]),
                    'leverage': row[5],
                    'side': row[6],
                    'fee': float(row[7]),
                    'profit': float(row[8]),
                    'created_at': row[10]
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
        with self.conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO conversations (model_id, prompt, response)
                VALUES (%s, %s, %s)
            ''', (model_id, prompt, response))
            self.conn.commit()
    
    def get_conversations(self, model_id: int = None, limit: int = 20) -> List[Dict]:
        """
        获取对话记录
        
        Args:
            model_id: 模型ID，如果为None则获取所有模型的对话记录
            limit: 返回记录数量限制，默认为20
            
        Returns:
            list: 对话记录列表
        """
        with self.conn.cursor() as cursor:
            if model_id is not None:
                cursor.execute('''
                    SELECT id, model_id, prompt, response, created_at
                    FROM conversations 
                    WHERE model_id = %s 
                    ORDER BY created_at DESC 
                    LIMIT %s
                ''', (model_id, limit))
            else:
                cursor.execute('''
                    SELECT id, model_id, prompt, response, created_at
                    FROM conversations 
                    ORDER BY created_at DESC 
                    LIMIT %s
                ''', (limit,))
            
            rows = cursor.fetchall()
            conversations = []
            for row in rows:
                conversations.append({
                    'id': row[0],
                    'model_id': row[1],
                    'prompt': row[2],
                    'response': row[3],
                    'created_at': row[4]
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
        with self.conn.cursor() as cursor:
            cursor.execute('''
                INSERT INTO account_values (model_id, total_value, cash, positions_value)
                VALUES (%s, %s, %s, %s)
            ''', (model_id, total_value, cash, positions_value))
            self.conn.commit()
    
    def get_account_value_history(self, model_id: int, limit: int = 100) -> List[Dict]:
        """
        获取账户价值历史记录
        
        Args:
            model_id: 模型ID
            limit: 返回记录数量限制，默认为100
            
        Returns:
            list: 账户价值历史记录列表
        """
        with self.conn.cursor() as cursor:
            cursor.execute('''
                SELECT id, model_id, total_value, cash, positions_value, created_at
                FROM account_values 
                WHERE model_id = %s 
                ORDER BY created_at DESC 
                LIMIT %s
            ''', (model_id, limit))
            
            rows = cursor.fetchall()
            history = []
            for row in rows:
                history.append({
                    'id': row[0],
                    'model_id': row[1],
                    'total_value': float(row[2]),
                    'cash': float(row[3]),
                    'positions_value': float(row[4]),
                    'created_at': row[5]
                })
            
            return history
    
    def get_aggregated_account_value_history(self, days: int = 30) -> List[Dict]:
        """
        获取聚合的账户价值历史记录（按模型分组）
        
        Args:
            days: 天数限制，默认为30天
            
        Returns:
            list: 聚合的账户价值历史记录列表
        """
        with self.conn.cursor() as cursor:
            cursor.execute('''
                SELECT 
                    DATE(created_at) as date,
                    model_id,
                    AVG(total_value) as avg_total_value,
                    AVG(cash) as avg_cash,
                    AVG(positions_value) as avg_positions_value
                FROM account_values 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY DATE(created_at), model_id
                ORDER BY date DESC
            ''', (days,))
            
            rows = cursor.fetchall()
            history = []
            for row in rows:
                history.append({
                    'date': row[0],
                    'model_id': row[1],
                    'avg_total_value': float(row[2]),
                    'avg_cash': float(row[3]),
                    'avg_positions_value': float(row[4])
                })
            
            return history
    
    def get_multi_model_chart_data(self, days: int = 30) -> Dict:
        """
        获取多模型图表数据
        
        Args:
            days: 天数限制，默认为30天
            
        Returns:
            dict: 多模型图表数据
        """
        with self.conn.cursor() as cursor:
            # 获取最近N天的日期范围
            cursor.execute('''
                SELECT DATE(MIN(created_at)) as min_date, DATE(MAX(created_at)) as max_date
                FROM account_values 
                WHERE created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
            ''', (days,))
            
            date_range = cursor.fetchone()
            if not date_range or not date_range[0]:
                return {}
            
            min_date, max_date = date_range[0], date_range[1]
            
            # 获取所有模型的数据
            cursor.execute('''
                SELECT 
                    DATE(a.created_at) as date,
                    a.model_id,
                    m.name as model_name,
                    AVG(a.total_value) as avg_total_value
                FROM account_values a
                JOIN models m ON a.model_id = m.id
                WHERE a.created_at >= DATE_SUB(NOW(), INTERVAL %s DAY)
                GROUP BY DATE(a.created_at), a.model_id, m.name
                ORDER BY date, a.model_id
            ''', (days,))
            
            rows = cursor.fetchall()
            
            # 组织数据结构
            chart_data = {
                'dates': [],
                'models': {}
            }
            
            # 收集所有日期
            dates = set()
            model_data = {}
            
            for row in rows:
                date = row[0]
                model_id = row[1]
                model_name = row[2]
                avg_value = float(row[3])
                
                dates.add(date)
                
                if model_id not in model_data:
                    model_data[model_id] = {
                        'name': model_name,
                        'values': {}
                    }
                
                model_data[model_id]['values'][date] = avg_value
            
            # 排序日期
            chart_data['dates'] = sorted(list(dates))
            
            # 为每个模型填充数据
            for model_id, data in model_data.items():
                chart_data['models'][model_id] = {
                    'name': data['name'],
                    'values': []
                }
                
                for date in chart_data['dates']:
                    value = data['values'].get(date, None)
                    chart_data['models'][model_id]['values'].append(value)
            
            return chart_data
    
    def get_settings(self) -> Dict:
        """
        获取系统设置
        
        Returns:
            dict: 系统设置字典
        """
        with self.conn.cursor() as cursor:
            cursor.execute('''
                SELECT trading_frequency_minutes, trading_fee_rate, created_at, updated_at
                FROM settings 
                ORDER BY id DESC 
                LIMIT 1
            ''')
            
            row = cursor.fetchone()
            if row:
                return {
                    'trading_frequency_minutes': row[0],
                    'trading_fee_rate': float(row[1]),
                    'created_at': row[2],
                    'updated_at': row[3]
                }
            else:
                # 如果没有设置记录，返回默认值
                return {
                    'trading_frequency_minutes': 60,
                    'trading_fee_rate': 0.001,
                    'created_at': None,
                    'updated_at': None
                }
    
    def update_settings(self, settings: Dict):
        """
        更新系统设置
        
        Args:
            settings (Dict): 新的设置值
        """
        with self.conn.cursor() as cursor:
            # 更新系统设置
            cursor.execute('''
                UPDATE settings 
                SET trading_frequency_minutes = %s, trading_fee_rate = %s, updated_at = CURRENT_TIMESTAMP
            ''', (settings.get('trading_frequency_minutes', 60), 
                  settings.get('trading_fee_rate', 0.001)))
            
            # 如果没有更新任何记录，则插入新记录
            if cursor.rowcount == 0:
                cursor.execute('''
                    INSERT INTO settings (trading_frequency_minutes, trading_fee_rate)
                    VALUES (%s, %s)
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
        with self.conn.cursor() as cursor:
            # 插入提供商信息
            cursor.execute('''
                INSERT INTO providers (name, api_key, api_url)
                VALUES (%s, %s, %s)
            ''', (name, api_key, api_url))
            
            # 提交事务并返回新记录的ID
            self.conn.commit()
            return cursor.lastrowid
    
    def get_provider(self, provider_id: int) -> Optional[Dict]:
        """
        获取API提供商信息
        
        Args:
            provider_id: 提供商ID
            
        Returns:
            dict or None: 提供商信息字典或None（如果未找到）
        """
        with self.conn.cursor() as cursor:
            cursor.execute('''
                SELECT id, name, api_key, api_url, created_at
                FROM providers 
                WHERE id = %s
            ''', (provider_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'api_key': row[2],
                    'api_url': row[3],
                    'created_at': row[4]
                }
            return None
    
    def get_all_providers(self) -> List[Dict]:
        """
        获取所有API提供商信息
        
        Returns:
            List[Dict]: 所有提供商信息列表
        """
        with self.conn.cursor() as cursor:
            # 查询所有提供商信息
            cursor.execute('SELECT * FROM providers ORDER BY created_at DESC')
            rows = cursor.fetchall()
            
            # 构建提供商信息列表
            providers = []
            for row in rows:
                providers.append({
                    'id': row[0],
                    'name': row[1],
                    'api_key': row[2],
                    'api_url': row[3],
                    'created_at': row[4]
                })
            
            return providers
    
    def delete_provider(self, provider_id: int) -> bool:
        """
        删除API提供商
        
        Args:
            provider_id: 要删除的提供商ID
            
        Returns:
            bool: 删除成功返回True，否则返回False
        """
        with self.conn.cursor() as cursor:
            cursor.execute('DELETE FROM providers WHERE id = %s', (provider_id,))
            self.conn.commit()
            return cursor.rowcount > 0
    
    def update_provider(self, provider_id: int, name: str, api_key: str, api_url: str) -> bool:
        """
        更新API提供商信息
        
        Args:
            provider_id: 要更新的提供商ID
            name: 新的提供商名称
            api_key: 新的API密钥
            api_url: 新的API地址
            
        Returns:
            bool: 更新成功返回True，否则返回False
        """
        with self.conn.cursor() as cursor:
            cursor.execute('''
                UPDATE providers 
                SET name = %s, api_key = %s, api_url = %s
                WHERE id = %s
            ''', (name, api_key, api_url, provider_id))
            self.conn.commit()
            return cursor.rowcount > 0
    
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
        with self.conn.cursor() as cursor:
            # 插入模型信息
            cursor.execute('''
                INSERT INTO models (name, provider_id, model_name, description, initial_capital)
                VALUES (%s, %s, %s, %s, %s)
            ''', (name, provider_id, model_name, description, initial_capital))
            
            # 提交事务并返回新记录的ID
            self.conn.commit()
            return cursor.lastrowid
    
    def get_model(self, model_id: int) -> Optional[Dict]:
        """
        获取AI模型配置信息
        
        Args:
            model_id: 模型ID
            
        Returns:
            dict or None: 模型信息字典或None（如果未找到）
        """
        with self.conn.cursor() as cursor:
            cursor.execute('''
                SELECT m.id, m.name, m.provider_id, m.model_name, m.description, m.initial_capital,
                       m.created_at, p.api_key, p.api_url, p.name as provider_name
                FROM models m
                JOIN providers p ON m.provider_id = p.id
                WHERE m.id = %s
            ''', (model_id,))
            
            row = cursor.fetchone()
            if row:
                return {
                    'id': row[0],
                    'name': row[1],
                    'provider_id': row[2],
                    'model_name': row[3],
                    'description': row[4],
                    'initial_capital': row[5],
                    'created_at': row[6],
                    'api_key': row[7],
                    'api_url': row[8],
                    'provider_name': row[9]
                }
            return None
    
    def get_all_models(self) -> List[Dict]:
        """
        获取所有交易模型信息

        Returns:
            List[Dict]: 所有模型信息列表
        """
        with self.conn.cursor() as cursor:
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
                    'id': row[0],
                    'name': row[1],
                    'provider_id': row[2],
                    'provider_name': row[3],
                    'model_name': row[4],
                    'description': row[5],
                    'initial_capital': row[6],
                    'created_at': row[7],
                    'api_key': row[8],
                    'api_url': row[9]
                })
            
            return models
    
    def get_leaderboard(self) -> List[Dict]:
        """
        获取排行榜信息
        
        Returns:
            List[Dict]: 排行榜信息列表
        """
        with self.conn.cursor() as cursor:
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
                    'model_id': row[0],
                    'model_name': row[1],
                    'initial_capital': row[2],
                    'account_value': row[3] or row[2],
                    'returns_percent': row[4] or 0
                })
            
            return leaderboard

