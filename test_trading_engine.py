"""
TradingEngine类的测试文件
"""

import unittest
from unittest.mock import Mock, patch
from trading_engine import TradingEngine
from database import Database
from market_data import MarketDataFetcher
from ai_trader import AITrader


class TestTradingEngineBuildAccountInfo(unittest.TestCase):
    """测试TradingEngine类的_build_account_info方法"""
    
    def setUp(self):
        """测试前的准备工作"""
        # 创建模拟对象
        self.mock_db = Mock(spec=Database)
        self.mock_market_fetcher = Mock(spec=MarketDataFetcher)
        self.mock_ai_trader = Mock(spec=AITrader)
        
        # 创建TradingEngine实例
        self.trading_engine = TradingEngine(
            model_id="test_model",
            db=self.mock_db,
            market_fetcher=self.mock_market_fetcher,
            ai_trader=self.mock_ai_trader
        )
    
    def test_build_account_info_with_empty_portfolio(self):
        """测试空投资组合的账户信息构建"""
        # 设置模拟返回值
        self.mock_db.get_portfolio.return_value = {'cash': 10000}
        self.mock_market_fetcher.get_current_price.return_value = None
        
        # 调用被测试的方法
        account_info = self.trading_engine._build_account_info()
        
        # 验证结果
        self.assertEqual(account_info['cash_balance'], 10000)
        self.assertEqual(account_info['total_position_value'], 0)
        self.assertEqual(account_info['total_value'], 10000)
        self.assertEqual(account_info['total_return'], 0)
        self.assertEqual(account_info['portfolio'], {'cash': 10000})
    
    def test_build_account_info_with_positions(self):
        """测试有持仓的账户信息构建"""
        # 设置模拟返回值
        portfolio = {
            'cash': 5000,
            'BTC': {'quantity': 1, 'avg_price': 40000},
            'ETH': {'quantity': 10, 'avg_price': 2000}
        }
        self.mock_db.get_portfolio.return_value = portfolio
        
        # 设置市场价格模拟返回值
        self.mock_market_fetcher.get_current_price.side_effect = [
            {'price': 50000, 'change_24h': 5},  # BTC价格
            {'price': 2500, 'change_24h': 3}    # ETH价格
        ]
        
        # 调用被测试的方法
        account_info = self.trading_engine._build_account_info()
        
        # 验证结果
        self.assertEqual(account_info['cash_balance'], 5000)
        self.assertEqual(account_info['total_position_value'], 75000)  # BTC: 1*50000 + ETH: 10*2500
        self.assertEqual(account_info['total_value'], 80000)  # 5000 + 75000
        self.assertEqual(account_info['total_return'], 700)  # ((80000-10000)/10000)*100
        
        # 验证portfolio中的持仓信息是否更新
        self.assertIn('current_value', account_info['portfolio']['BTC'])
        self.assertIn('current_price', account_info['portfolio']['BTC'])
        self.assertIn('current_value', account_info['portfolio']['ETH'])
        self.assertIn('current_price', account_info['portfolio']['ETH'])
        
        self.assertEqual(account_info['portfolio']['BTC']['current_value'], 50000)
        self.assertEqual(account_info['portfolio']['BTC']['current_price'], 50000)
        self.assertEqual(account_info['portfolio']['ETH']['current_value'], 25000)
        self.assertEqual(account_info['portfolio']['ETH']['current_price'], 2500)
    
    def test_build_account_info_with_zero_quantity_positions(self):
        """测试持仓数量为零的账户信息构建"""
        # 设置模拟返回值
        portfolio = {
            'cash': 10000,
            'BTC': {'quantity': 0, 'avg_price': 40000}
        }
        self.mock_db.get_portfolio.return_value = portfolio
        self.mock_market_fetcher.get_current_price.return_value = None
        
        # 调用被测试的方法
        account_info = self.trading_engine._build_account_info()
        
        # 验证结果
        self.assertEqual(account_info['cash_balance'], 10000)
        self.assertEqual(account_info['total_position_value'], 0)
        self.assertEqual(account_info['total_value'], 10000)
        self.assertEqual(account_info['total_return'], 0)
    
    def test_build_account_info_with_no_cash(self):
        """测试没有现金余额的账户信息构建"""
        # 设置模拟返回值
        portfolio = {
            'BTC': {'quantity': 1, 'avg_price': 40000}
        }
        self.mock_db.get_portfolio.return_value = portfolio
        
        # 设置市场价格模拟返回值
        self.mock_market_fetcher.get_current_price.return_value = {
            'price': 50000, 
            'change_24h': 5
        }
        
        # 调用被测试的方法
        account_info = self.trading_engine._build_account_info()
        
        # 验证结果
        self.assertEqual(account_info['cash_balance'], 0)  # 默认为0
        self.assertEqual(account_info['total_position_value'], 50000)
        self.assertEqual(account_info['total_value'], 50000)
        self.assertEqual(account_info['total_return'], 400)  # ((50000-10000)/10000)*100
    
    def test_build_account_info_with_negative_return(self):
        """测试负收益的账户信息构建"""
        # 设置模拟返回值
        portfolio = {
            'cash': 5000,
            'BTC': {'quantity': 1, 'avg_price': 40000}
        }
        self.mock_db.get_portfolio.return_value = portfolio
        
        # 设置市场价格模拟返回值（低于购买价格）
        self.mock_market_fetcher.get_current_price.return_value = {
            'price': 30000, 
            'change_24h': -5
        }
        
        # 调用被测试的方法
        account_info = self.trading_engine._build_account_info()
        
        # 验证结果
        self.assertEqual(account_info['cash_balance'], 5000)
        self.assertEqual(account_info['total_position_value'], 30000)
        self.assertEqual(account_info['total_value'], 35000)
        self.assertEqual(account_info['total_return'], 250)  # ((35000-10000)/10000)*100
    
    def test_build_account_info_with_market_data_failure(self):
        """测试市场价格数据获取失败的情况"""
        # 设置模拟返回值
        portfolio = {
            'cash': 10000,
            'BTC': {'quantity': 1, 'avg_price': 40000}
        }
        self.mock_db.get_portfolio.return_value = portfolio
        
        # 模拟市场价格获取失败
        self.mock_market_fetcher.get_current_price.return_value = None
        
        # 调用被测试的方法
        account_info = self.trading_engine._build_account_info()
        
        # 验证结果
        self.assertEqual(account_info['cash_balance'], 10000)
        self.assertEqual(account_info['total_position_value'], 0)  # 由于价格获取失败，持仓价值为0
        self.assertEqual(account_info['total_value'], 10000)
        self.assertEqual(account_info['total_return'], 0)
    
    def test_build_account_info_with_leverage_and_side(self):
        """测试包含杠杆和方向信息的持仓"""
        # 设置模拟返回值
        portfolio = {
            'cash': 5000,
            'BTC': {'quantity': 1, 'avg_price': 40000, 'leverage': 2, 'side': 'long'}
        }
        self.mock_db.get_portfolio.return_value = portfolio
        
        # 设置市场价格模拟返回值
        self.mock_market_fetcher.get_current_price.return_value = {
            'price': 50000, 
            'change_24h': 5
        }
        
        # 调用被测试的方法
        account_info = self.trading_engine._build_account_info()
        
        # 验证结果
        self.assertEqual(account_info['cash_balance'], 5000)
        self.assertEqual(account_info['total_position_value'], 50000)
        self.assertEqual(account_info['total_value'], 55000)
        self.assertEqual(account_info['total_return'], 450)  # ((55000-10000)/10000)*100
        
        # 验证portfolio中的额外信息
        self.assertEqual(account_info['portfolio']['BTC']['leverage'], 2)
        self.assertEqual(account_info['portfolio']['BTC']['side'], 'long')


if __name__ == '__main__':
    unittest.main()