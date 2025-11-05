"""
AI测试接口模块

该模块提供了一套专门用于测试数据库查询功能的API接口。
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
import sys
import os
from trading_engine import TradingEngine

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入数据库模块
from database import Database
from config import Config

# 初始化Flask应用
app = Flask(__name__)
CORS(app)

# 初始化数据库连接
db = None
try:
    db_config = Config.DATABASE_CONFIG
    # 使用正确的数据库凭据
    db = Database(
        host=db_config['host'],
        port=db_config['port'],
        user=db_config['user'],
        password=db_config['password'],  # 使用config.py中的密码'123456'
        database=db_config['database']  # 使用config.py中的数据库名'trading_game'
    )
    print("Database connection established successfully")
except Exception as e:
    print(f"Warning: Database connection failed: {e}")
    print("Some API endpoints may not work properly")
    db = None

# ==================== 测试接口 ====================

@app.route('/')
def index():
    """
    测试接口首页
    
    Returns:
        JSON: 欢迎信息和可用接口列表
    """
    return jsonify({
        "message": "AI Trade Game - 数据库测试接口",
        "available_endpoints": [
            "GET /api/test/portfolio",
            "GET /api/test/trades",
            "GET /api/test/conversations",
            "GET /api/test/account-values",
            "GET /api/test/providers",
            "GET /api/test/models",
            "GET /api/test/settings",
            "GET /api/test/leaderboard"
        ]
    })

@app.route('/api/test/portfolio')
def test_get_portfolio():
    """
    测试获取投资组合信息
    
    Returns:
        JSON: 投资组合信息
    """
    if db is None:
        return jsonify({
            "success": False,
            "error": "Database connection not available"
        }), 500
        
    try:
        model_id = request.args.get('model_id', type=int)
        portfolio = db.get_portfolio(model_id)
        return jsonify({
            "success": True,
            "data": portfolio
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/test/trades')
def test_get_trades():
    """
    测试获取交易历史记录
    
    Returns:
        JSON: 交易历史记录
    """
    if db is None:
        return jsonify({
            "success": False,
            "error": "Database connection not available"
        }), 500
        
    try:
        model_id = request.args.get('model_id', type=int)
        limit = request.args.get('limit', 50, type=int)
        trades = db.get_trades(model_id, limit)
        return jsonify({
            "success": True,
            "data": trades
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/test/conversations')
def test_get_conversations():
    """
    测试获取对话记录
    
    Returns:
        JSON: 对话记录
    """
    if db is None:
        return jsonify({
            "success": False,
            "error": "Database connection not available"
        }), 500
        
    try:
        model_id = request.args.get('model_id', type=int)
        limit = request.args.get('limit', 20, type=int)
        conversations = db.get_conversations(model_id, limit)
        return jsonify({
            "success": True,
            "data": conversations
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/test/account-values')
def test_get_account_values():
    """
    测试获取账户价值历史记录
    
    Returns:
        JSON: 账户价值历史记录
    """
    if db is None:
        return jsonify({
            "success": False,
            "error": "Database connection not available"
        }), 500
        
    try:
        model_id = request.args.get('model_id', type=int)
        limit = request.args.get('limit', 100, type=int)
        if model_id is None:
            return jsonify({
                "success": False,
                "error": "model_id参数是必需的"
            }), 400
            
        history = db.get_account_value_history(model_id, limit)
        return jsonify({
            "success": True,
            "data": history
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/test/providers')
def test_get_providers():
    """
    测试获取所有API提供商信息
    
    Returns:
        JSON: API提供商信息列表
    """
    if db is None:
        return jsonify({
            "success": False,
            "error": "Database connection not available"
        }), 500
        
    try:
        providers = db.get_all_providers()
        return jsonify({
            "success": True,
            "data": providers
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/test/models')
def test_get_models():
    """
    测试获取所有交易模型信息
    
    Returns:
        JSON: 交易模型信息列表
    """
    if db is None:
        return jsonify({
            "success": False,
            "error": "Database connection not available"
        }), 500
        
    try:
        models = db.get_all_models()
        return jsonify({
            "success": True,
            "data": models
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/test/settings')
def test_get_settings():
    """
    测试获取系统设置
    
    Returns:
        JSON: 系统设置信息
    """
    if db is None:
        return jsonify({
            "success": False,
            "error": "Database connection not available"
        }), 500
        
    try:
        settings = db.get_settings()
        return jsonify({
            "success": True,
            "data": settings
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/test/leaderboard')
def test_get_leaderboard():
    """
    测试获取排行榜信息
    
    Returns:
        JSON: 排行榜信息
    """
    if db is None:
        return jsonify({
            "success": False,
            "error": "Database connection not available"
        }), 500
        
    try:
        leaderboard = db.get_leaderboard()
        return jsonify({
            "success": True,
            "data": leaderboard
        })
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/test/provider/<int:provider_id>')
def test_get_provider(provider_id):
    """
    测试获取单个API提供商信息
    
    Args:
        provider_id (int): 提供商ID
        
    Returns:
        JSON: API提供商信息
    """
    if db is None:
        return jsonify({
            "success": False,
            "error": "Database connection not available"
        }), 500
        
    try:
        provider = db.get_provider(provider_id)
        if provider:
            return jsonify({
                "success": True,
                "data": provider
            })
        else:
            return jsonify({
                "success": False,
                "error": "Provider not found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/test/model/<int:model_id>')
def test_get_model(model_id):
    """
    测试获取单个交易模型信息
    
    Args:
        model_id (int): 模型ID
        
    Returns:
        JSON: 交易模型信息
    """
    if db is None:
        return jsonify({
            "success": False,
            "error": "Database connection not available"
        }), 500
        
    try:
        model = db.get_model(model_id)
        if model:
            return jsonify({
                "success": True,
                "data": model
            })
        else:
            return jsonify({
                "success": False,
                "error": "Model not found"
            }), 404
    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

if __name__ == '__main__':
    """
    应用主入口
    """
    print("Starting AI Test API server...")
    print(f"Server running on http://localhost:{Config.PORT}")
    app.run(host=Config.HOST, port=Config.PORT, debug=Config.DEBUG)