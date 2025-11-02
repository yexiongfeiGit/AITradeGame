"""
配置文件示例

该文件包含了AITradeGame项目的所有配置项。用户需要创建一个config.py文件，
并复制此文件的内容到config.py中，然后根据自己的需求修改配置值。

配置项包括：
1. 服务器配置（主机、端口、调试模式）
2. 数据库配置（数据库文件路径）
3. 交易设置（自动交易开关、交易间隔、交易币种列表）
4. 市场数据配置（API缓存时间、API URL）
5. 前端刷新频率设置
6. 交易费率设置
"""

# 服务器配置
# HOST: 服务器监听的主机地址，'0.0.0.0'表示监听所有网络接口
# PORT: 服务器监听的端口号
# DEBUG: 调试模式开关，开发时可设为True，生产环境应设为False
HOST = '0.0.0.0'
PORT = 5000
DEBUG = True

# 数据库配置
# DATABASE_PATH: SQLite数据库文件的路径
DATABASE_PATH = 'aitrade.db'

# 交易设置
# AUTO_TRADING: 自动交易开关，True表示启用自动交易，False表示禁用
# TRADING_INTERVAL: 交易间隔（秒），自动交易时每隔多少秒执行一次交易循环
# COINS: 交易币种列表，包含所有需要交易的加密货币符号
AUTO_TRADING = False
TRADING_INTERVAL = 60
COINS = ['BTC', 'ETH', 'SOL', 'BNB', 'XRP', 'DOGE']

# 市场数据配置
# MARKET_API_CACHE: 市场数据API缓存时间（秒），避免频繁调用API
# MARKET_API_URL: 市场数据API的基础URL
MARKET_API_CACHE = 5
MARKET_API_URL = 'https://api.binance.com'

# 前端刷新频率（毫秒）
# MARKET_REFRESH: 市场数据刷新频率
# PORTFOLIO_REFRESH: 投资组合数据刷新频率
MARKET_REFRESH = 5000
PORTFOLIO_REFRESH = 3000

# 交易费率
# TRADE_FEE_RATE: 交易费率，0.001表示0.1%的双向收费（买入和卖出各收0.1%）
TRADE_FEE_RATE = 0.001

