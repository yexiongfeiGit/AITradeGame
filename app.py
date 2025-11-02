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
from flask import Flask, jsonify, request
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
    db = Database(Config.DATABASE_PATH)
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

@app.route('/api/providers', methods=['GET'])
def get_providers():
    """
    获取所有API提供商信息
    
    返回数据库中存储的所有API提供商信息列表。
    
    Returns:
        JSON: 包含提供商信息的响应对象
    """
    providers = db.get_all_providers()
    return jsonify(providers)

@app.route('/api/providers', methods=['POST'])
def add_provider():
    """
    添加新的API提供商
    
    从请求体中获取提供商信息并保存到数据库。
    
    Returns:
        JSON: 操作结果响应对象
    """
    data = request.json
    provider_id = db.add_provider(data['name'], data['api_key'], data['api_url'])
    return jsonify({'id': provider_id}), 201

@app.route('/api/providers/<int:provider_id>', methods=['PUT'])
def update_provider(provider_id):
    """
    更新指定的API提供商信息
    
    根据提供商ID更新其在数据库中的信息。
    
    Args:
        provider_id (int): 要更新的提供商ID
        
    Returns:
        JSON: 操作结果响应对象
    """
    data = request.json
    db.update_provider(provider_id, data['name'], data['api_key'], data['api_url'])
    return jsonify({'message': 'Provider updated'})

@app.route('/api/providers/<int:provider_id>', methods=['DELETE'])
def delete_provider(provider_id):
    """
    删除指定的API提供商
    
    根据提供商ID从数据库中删除对应记录。
    
    Args:
        provider_id (int): 要删除的提供商ID
        
    Returns:
        JSON: 操作结果响应对象
    """
    db.delete_provider(provider_id)
    return jsonify({'message': 'Provider deleted'})

@app.route('/api/models', methods=['GET'])
def get_models():
    """
    获取所有交易模型信息
    
    返回数据库中存储的所有交易模型信息列表，包括关联的提供商信息。
    
    Returns:
        JSON: 包含模型信息的响应对象
    """
    models = db.get_all_models()
    return jsonify(models)

@app.route('/api/models', methods=['POST'])
def add_model():
    """
    添加新的交易模型
    
    从请求体中获取模型信息并保存到数据库。
    
    Returns:
        JSON: 操作结果响应对象
    """
    data = request.json
    model_id = db.add_model(
        data['name'], 
        data['provider_id'], 
        data['model_name'], 
        data['description']
    )
    return jsonify({'id': model_id}), 201

@app.route('/api/models/chart-data')
def get_models_chart_data():
    """
    获取模型图表数据
    
    返回用于绘制模型性能图表的数据，包括账户价值历史记录。
    
    Returns:
        JSON: 包含图表数据的响应对象
    """
    days = request.args.get('days', 30, type=int)
    chart_data = db.get_multi_model_chart_data(days)
    return jsonify(chart_data)

@app.route('/api/portfolio')
def get_portfolio():
    """
    获取投资组合信息
    
    返回当前投资组合的状态，包括现金、总价值和各币种持仓情况。
    
    Returns:
        JSON: 包含投资组合信息的响应对象
    """
    portfolio = db.get_portfolio()
    return jsonify(portfolio)

@app.route('/api/market/prices')
def get_market_prices():
    """
    获取市场价格信息
    
    从市场数据获取器获取实时价格信息，包括24小时价格变化。
    
    Returns:
        JSON: 包含市场价格信息的响应对象
    """
    prices = market_fetcher.get_prices()
    return jsonify(prices)

@app.route('/api/models/<int:model_id>/execute', methods=['POST'])
def execute_model(model_id):
    """
    执行指定的交易模型
    
    触发指定模型的一次交易循环，生成并执行交易决策。
    
    Args:
        model_id (int): 要执行的模型ID
        
    Returns:
        JSON: 包含执行结果的响应对象
    """
    if model_id not in trading_engines:
        return jsonify({'error': 'Model not found'}), 404
    
    try:
        # 执行交易循环
        result = trading_engines[model_id].execute_trading_cycle()
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/trades/history')
def get_trade_history():
    """
    获取交易历史记录
    
    返回数据库中存储的所有交易历史记录。
    
    Returns:
        JSON: 包含交易历史的响应对象
    """
    trades = db.get_trades()
    return jsonify(trades)

@app.route('/api/conversations')
def get_conversations():
    """
    获取对话历史记录
    
    返回AI交易器与模型之间的对话历史记录。
    
    Returns:
        JSON: 包含对话历史的响应对象
    """
    conversations = db.get_conversations()
    return jsonify(conversations)

@app.route('/api/account-value-history')
def get_account_value_history():
    """
    获取账户价值历史记录
    
    返回账户价值随时间变化的历史记录，用于绘制收益曲线。
    
    Returns:
        JSON: 包含账户价值历史的响应对象
    """
    days = request.args.get('days', 30, type=int)
    history = db.get_aggregated_account_value_history(days)
    return jsonify(history)

@app.route('/api/leaderboard')
def get_leaderboard():
    """
    获取排行榜信息
    
    返回基于模型收益率的排行榜信息。
    
    Returns:
        JSON: 包含排行榜信息的响应对象
    """
    leaderboard = db.get_leaderboard()
    return jsonify(leaderboard)

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """
    获取系统设置
    
    返回当前系统的配置设置信息。
    
    Returns:
        JSON: 包含系统设置的响应对象
    """
    settings = db.get_settings()
    return jsonify(settings)

@app.route('/api/settings', methods=['POST'])
def update_settings():
    """
    更新系统设置
    
    从请求体中获取新的设置值并更新数据库中的记录。
    
    Returns:
        JSON: 操作结果响应对象
    """
    data = request.json
    db.update_settings(data)
    return jsonify({'message': 'Settings updated'})

# ==================== 自动交易循环 ====================

def trading_loop():
    """
    自动交易循环函数
    
    在单独的线程中运行，定期执行所有交易引擎的交易循环。
    这是实现自动交易的核心函数。
    """
    while True:
        try:
            # 遍历所有交易引擎并执行交易循环
            for coin, engine in trading_engines.items():
                engine.execute_trading_cycle()
            
            # 等待下一个交易周期
            import time
            time.sleep(Config.TRADING_INTERVAL)
        except KeyboardInterrupt:
            # 处理键盘中断（程序退出）
            print("Trading loop interrupted by user")
            break
        except Exception as e:
            # 处理其他异常，避免程序崩溃
            print(f"Error in trading loop: {e}")
            import traceback
            traceback.print_exc()
            # 出错后短暂等待再继续
            time.sleep(5)

# ==================== 系统管理功能 ====================

@app.route('/api/version')
def get_version():
    """
    获取应用版本信息
    
    返回当前应用的版本号等信息。
    
    Returns:
        JSON: 包含版本信息的响应对象
    """
    return jsonify({
        'version': __version__,
        'repo': __repo__,
        'owner': __github_owner__
    })

@app.route('/api/check-update')
def check_update():
    """
    检查是否有新版本可用
    
    通过访问GitHub API检查是否有比当前版本更新的发布版本。
    
    Returns:
        JSON: 包含更新检查结果的响应对象
    """
    try:
        import requests
        
        # GitHub releases API地址
        url = f"https://api.github.com/repos/{__github_owner__}/{__repo__}/releases/latest"
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        
        # 解析响应数据
        data = response.json()
        latest_version = data['tag_name'].lstrip('v')  # 移除版本号前的'v'
        
        # 比较版本号
        has_update = compare_versions(latest_version, __version__)
        
        return jsonify({
            'has_update': has_update,
            'latest_version': latest_version,
            'current_version': __version__,
            'release_notes': data.get('body', ''),
            'download_url': data.get('html_url', '')
        })
    except Exception as e:
        # 处理检查更新过程中的异常
        print(f"Update check failed: {e}")
        return jsonify({'has_update': False, 'error': str(e)})

def compare_versions(v1, v2):
    """
    比较两个版本号
    
    Args:
        v1 (str): 第一个版本号
        v2 (str): 第二个版本号
        
    Returns:
        bool: 如果v1大于v2则返回True，否则返回False
    """
    # 将版本号分割为数字部分进行比较
    parts1 = [int(x) for x in v1.split('.')]
    parts2 = [int(x) for x in v2.split('.')]
    
    # 逐位比较版本号
    for i in range(max(len(parts1), len(parts2))):
        # 获取对应位置的版本号部分，如果不存在则默认为0
        p1 = parts1[i] if i < len(parts1) else 0
        p2 = parts2[i] if i < len(parts2) else 0
        
        # 如果发现不同部分，直接返回比较结果
        if p1 > p2:
            return True
        elif p1 < p2:
            return False
    
    # 版本号完全相同
    return False

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

if __name__ == '__main__':
    """
    应用主入口
    
    负责初始化所有组件、启动自动交易线程和运行Flask应用。
    """
    print(f"Starting AI Trade Game v{__version__}...")
    
    # 初始化核心组件
    init_components()
    
    # 如果启用了自动交易，则启动交易循环线程
    if Config.AUTO_TRADING:
        trading_thread = threading.Thread(target=trading_loop, daemon=True)
        trading_thread.start()
        print("Auto trading loop started")
    
    # 初始化交易引擎
    init_trading_engines()
    
    # 如果不是在调试模式下运行，则自动打开浏览器
    if not Config.DEBUG:
        url = f"http://{Config.HOST}:{Config.PORT}"
        print(f"Opening browser to {url}")
        webbrowser.open(url)
    
    # 启动Flask应用
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)
