"""
AI炒币游戏主应用模块

该模块是AI炒币游戏的主入口，使用Flask框架构建Web应用。
它负责初始化核心组件、定义API路由、启动交易循环等主要功能。
"""

import os
import sys
import json
import sqlite3
import threading
import webbrowser
from datetime import datetime
from flask import Flask, jsonify, request, render_template
from flask_cors import CORS

# 导入项目模块
from database import Database
from market_data import MarketDataFetcher
from trading_engine import TradingEngine
from ai_trader import AITrader
from config import Config
from version import (__version__, __repo__, __github_owner__)

# 初始化Flask应用
app = Flask(__name__)
CORS(app)

# 全局变量声明
db = None
market_fetcher = None
trading_engines = {}
ai_traders = {}

def init_components():
    """
    初始化应用核心组件
    
    包括数据库连接、市场数据获取器、AI交易器和交易引擎等核心组件的初始化。
    这些组件在整个应用生命周期中会被重复使用。
    """
    global db, market_fetcher, trading_engines, ai_traders
    
    # 初始化数据库连接
    db_config = Config.DATABASE_CONFIG
    db = Database(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],
        database=db_config['database']
    )
    db.init_db()  # 创建数据库表
    
    # 初始化市场数据获取器
    market_fetcher = MarketDataFetcher(
        cache_duration=Config.MARKET_API_CACHE,
        api_url=Config.MARKET_API_URL
    )
    
    # 为每个配置的币种初始化AI交易器和交易引擎
    for coin in Config.COINS:
        # 创建AI交易器实例
        ai_traders[coin] = AITrader(
            api_key=Config.LLM_API_KEY,
            api_url=Config.LLM_API_URL,
            model_name=Config.LLM_MODEL_NAME
        )
        
        # 创建交易引擎实例
        trading_engines[coin] = TradingEngine(
            model_id=coin,
            db=db,
            market_fetcher=market_fetcher,
            ai_trader=ai_traders[coin],
            trade_fee_rate=Config.TRADE_FEE_RATE
        )

# ==================== API路由定义 ====================


def init_trading_engines():
    """
    初始化交易引擎
    
    为每个配置的币种创建并初始化对应的交易引擎实例。
    """
    global trading_engines
    
    # 遍历所有配置的币种
    for coin in Config.COINS:
        if coin not in trading_engines:
            # 创建新的交易引擎实例
            trading_engines[coin] = TradingEngine(
                model_id=coin,
                db=db,
                market_fetcher=market_fetcher,
                ai_trader=ai_traders[coin],
                trade_fee_rate=Config.TRADE_FEE_RATE
            )



@app.route('/test/btc', methods=['GET'])
def testBtc():
    """
    测试BTC交易
    
    模拟对BTC的交易操作，包括获取市场数据、生成交易指令和执行交易。
    """
    # 获取BTC当前市场数据
    btc_data = market_fetcher.get_market_data('BTCUSDT')
    print(f"BTC market data: {btc_data}")

    account_info = ai_traders['BTC'].build_account_info()
    print(f"BTC account info: {account_info}")  
    
   





if __name__ == '__main__':
    """
    应用主入口
    
    负责初始化所有组件、启动自动交易线程和运行Flask应用。
    """
    print(f"Starting AI Trade Game v{__version__}...")
    
    # 初始化核心组件
    init_components()
    

    
    # 启动Flask应用
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
