"""
交易引擎模块

该模块实现了自动交易的核心逻辑，负责：
1. 执行交易循环
2. 获取市场状态
3. 调用AI进行交易决策
4. 执行交易决策
5. 记录交易和账户价值

交易引擎是整个系统的核心组件，连接了市场数据、AI决策和数据库操作。
"""

from typing import Dict, List, Optional, Tuple
import time
import json
from datetime import datetime

# 从其他模块导入所需组件
from ai_trader import AITrader
from database import Database
from market_data import MarketDataFetcher

class TradingEngine:
    """
    交易引擎类
    
    该类封装了自动交易的所有核心逻辑，包括市场数据获取、
    AI决策调用、交易执行和账户管理等功能。
    """
    
    def __init__(self, model_id: str, db: Database, market_fetcher: MarketDataFetcher, 
                 ai_trader: AITrader, trade_fee_rate: float = 0.001):
        """
        初始化交易引擎
        
        Args:
            model_id (str): 交易模型ID
            db (Database): 数据库实例
            market_fetcher (MarketDataFetcher): 市场数据获取器实例
            ai_trader (AITrader): AI交易器实例
            trade_fee_rate (float): 交易费率，默认为0.001（0.1%）
        """
        self.model_id = model_id
        self.db = db
        self.market_fetcher = market_fetcher
        self.ai_trader = ai_trader
        self.trade_fee_rate = trade_fee_rate
    
    def execute_trading_cycle(self, coins: List[str]) -> bool:
        """
        执行一个交易周期
        
        这是交易引擎的核心方法，负责完成一个完整的交易循环：
        1. 获取市场状态
        2. 构建账户信息
        3. 调用AI进行交易决策
        4. 记录对话历史
        5. 执行交易决策
        6. 记录账户价值
        
        Args:
            coins (List[str]): 交易币种列表
            
        Returns:
            bool: 交易周期执行成功返回True，失败返回False
        """
        try:
            # 1. 获取市场状态
            market_state = self._get_market_state(coins)
            if not market_state:
                print("无法获取市场状态")
                return False
            
            # 2. 构建账户信息
            account_info = self.build_account_info()
            
            # 3. 格式化提示信息
            prompt = self._format_prompt(market_state, account_info)
            
            # 4. 调用AI进行交易决策
            decision_response = self.ai_trader.make_decision(prompt)
            
            # 5. 记录对话历史
            self.db.add_conversation(self.model_id, prompt, decision_response)
            
            # 6. 解析并执行交易决策
            decisions = self.ai_trader._parse_response(decision_response)
            self._execute_decisions(decisions, market_state)
            
            # 7. 记录账户价值快照
            self.db.record_account_value(self.model_id, account_info['total_value'])
            
            return True
        except Exception as e:
            print(f"交易周期执行失败: {e}")
            return False
    
    def _get_market_state(self, coins: List[str]) -> Optional[Dict]:
        """
        获取市场状态
        
        收集所有交易币种的当前价格和技术指标信息。
        
        Args:
            coins (List[str]): 交易币种列表
            
        Returns:
            Optional[Dict]: 市场状态字典，如果获取失败则返回None
        """
        market_data = {}
        
        for coin in coins:
            # 获取币种数据及技术指标
            data = self.market_fetcher.get_coin_data_with_indicators(coin)
            if data:
                market_data[coin] = data
            else:
                print(f"无法获取{coin}的市场数据")
                return None
        
        return market_data
    
    def build_account_info(self) -> Dict:
        """
        构建账户信息
        
        获取当前账户的持仓信息、现金余额和总价值，并计算收益率。
        
        Returns:
            Dict: 包含账户信息的字典
        """


        # 获取账户持仓
        print(f"model_id: {self.model_id}")

        portfolio = self.db.get_portfolio(self.model_id)
        print(f"portfolio: {portfolio}")
        # 获取现金余额
        cash_balance = portfolio.get('cash', 0)
        
        # 计算持仓价值
        total_position_value = 0
        for coin, position in portfolio.items():
            if coin != 'cash' and position['quantity'] > 0:
                # 获取当前价格
                price_data = self.market_fetcher.get_current_price(coin)
                if price_data:
                    current_price = price_data['price']
                    position_value = position['quantity'] * current_price
                    total_position_value += position_value
                    # 更新持仓信息中的当前价值
                    position['current_value'] = position_value
                    position['current_price'] = current_price
        
        # 计算总价值
        total_value = cash_balance + total_position_value
        
        # 计算总收益率
        initial_capital = 10000  # 初始资金假设为10000
        total_return = ((total_value - initial_capital) / initial_capital) * 100 if initial_capital > 0 else 0
        
        return {
            'portfolio': portfolio,
            'cash_balance': cash_balance,
            'total_position_value': total_position_value,
            'total_value': total_value,
            'total_return': total_return
        }
    
    def _format_prompt(self, market_state: Dict, account_info: Dict) -> str:
        """
        格式化提示信息
        
        将市场状态和账户信息格式化为AI模型可以理解的提示文本。
        
        Args:
            market_state (Dict): 市场状态信息
            account_info (Dict): 账户信息
            
        Returns:
            str: 格式化后的提示文本
        """
        # 格式化市场数据
        market_info_lines = []
        for coin, data in market_state.items():
            line = f"{coin}: 价格=${data['price']:.4f}, 24h变化={data['change_24h']:.2f}%, 7日变化={data['change_7d']:.2f}%"
            if data['sma_7']:
                line += f", SMA7=${data['sma_7']:.4f}"
            if data['sma_14']:
                line += f", SMA14=${data['sma_14']:.4f}"
            if data['rsi']:
                line += f", RSI={data['rsi']:.2f}"
            market_info_lines.append(line)
        
        market_info = "\n".join(market_info_lines)
        
        # 格式化账户信息
        portfolio_info_lines = []
        portfolio = account_info['portfolio']
        for coin, position in portfolio.items():
            if coin == 'cash':
                portfolio_info_lines.append(f"现金: ${position:.2f}")
            elif position['quantity'] > 0:
                line = f"{coin}: 数量={position['quantity']:.4f}"
                if 'current_value' in position:
                    line += f", 价值=${position['current_value']:.2f}"
                if 'current_price' in position:
                    line += f", 当前价格=${position['current_price']:.4f}"
                portfolio_info_lines.append(line)
        
        portfolio_info = "\n".join(portfolio_info_lines)
        
        # 构建完整提示文本
        prompt = f"""
你是一个专业的加密货币交易AI。请根据以下市场数据和账户信息，做出交易决策。

市场数据:
{market_info}

账户信息:
{portfolio_info}
总价值: ${account_info['total_value']:.2f}
总收益率: {account_info['total_return']:.2f}%

请以JSON格式回复你的交易决策，包含以下字段：
- action: 交易动作 ("buy", "sell", "close", "hold")
- coin: 交易币种 (如 "BTC", "ETH"等)
- amount: 交易数量 (如果是"hold"则为0)
- reason: 交易理由

示例:
{{
    "action": "buy",
    "coin": "BTC",
    "amount": 0.1,
    "reason": "BTC价格突破SMA7，预期上涨"
}}
"""
        
        return prompt.strip()
    
    def _execute_decisions(self, decisions: List[Dict], market_state: Dict):
        """
        执行交易决策
        
        根据AI的决策执行相应的交易操作。
        
        Args:
            decisions (List[Dict]): 交易决策列表
            market_state (Dict): 当前市场状态
        """
        for decision in decisions:
            action = decision.get('action', '').lower()
            coin = decision.get('coin', '')
            amount = decision.get('amount', 0)
            
            # 验证决策参数
            if not coin or amount < 0:
                print(f"无效的交易决策: {decision}")
                continue
            
            # 根据动作类型执行相应操作
            if action == 'buy':
                self._execute_buy(coin, amount, market_state[coin]['price'])
            elif action == 'sell':
                self._execute_sell(coin, amount, market_state[coin]['price'])
            elif action == 'close':
                self._execute_close(coin, amount)
            elif action == 'hold':
                print(f"持有 {coin}，不执行交易")
            else:
                print(f"未知的交易动作: {action}")
    
    def _execute_buy(self, coin: str, amount: float, price: float):
        """
        执行买入操作
        
        Args:
            coin (str): 买入币种
            amount (float): 买入数量
            price (float): 买入价格
        """
        # 计算买入所需保证金
        required_margin = amount * price
        
        # 获取账户现金余额
        portfolio = self.db.get_portfolio(self.model_id)
        cash_balance = portfolio.get('cash', 0)
        
        # 检查现金余额是否足够
        if cash_balance < required_margin:
            print(f"现金余额不足，无法买入 {amount} {coin}")
            return
        
        # 计算交易费用
        fee = required_margin * self.trade_fee_rate
        
        # 检查总费用是否超过余额
        total_cost = required_margin + fee
        if cash_balance < total_cost:
            print(f"余额不足支付交易费用，无法买入 {amount} {coin}")
            return
        
        # 更新现金余额
        new_cash_balance = cash_balance - total_cost
        self.db.update_portfolio(self.model_id, 'cash', new_cash_balance)
        
        # 更新币种持仓
        current_position = portfolio.get(coin, {'quantity': 0, 'avg_price': 0})
        current_quantity = current_position['quantity']
        current_avg_price = current_position['avg_price']
        
        # 计算新的平均价格
        total_value_before = current_quantity * current_avg_price
        total_value_after = total_value_before + required_margin
        new_quantity = current_quantity + amount
        new_avg_price = total_value_after / new_quantity if new_quantity > 0 else 0
        
        # 更新持仓
        self.db.update_portfolio(self.model_id, coin, new_quantity, new_avg_price)
        
        # 记录交易
        self.db.add_trade(self.model_id, coin, 'buy', amount, price, fee)
        
        print(f"成功买入 {amount} {coin}，价格 ${price:.4f}，费用 ${fee:.4f}")
    
    def _execute_sell(self, coin: str, amount: float, price: float):
        """
        执行卖出操作（做空）
        
        Args:
            coin (str): 卖出币种
            amount (float): 卖出数量
            price (float): 卖出价格
        """
        # 计算卖出获得的现金
        proceeds = amount * price
        
        # 计算交易费用
        fee = proceeds * self.trade_fee_rate
        
        # 更新现金余额
        portfolio = self.db.get_portfolio(self.model_id)
        cash_balance = portfolio.get('cash', 0)
        new_cash_balance = cash_balance + proceeds - fee
        self.db.update_portfolio(self.model_id, 'cash', new_cash_balance)
        
        # 记录交易
        self.db.add_trade(self.model_id, coin, 'sell', amount, price, fee)
        
        print(f"成功卖出 {amount} {coin}，价格 ${price:.4f}，费用 ${fee:.4f}")
    
    def _execute_close(self, coin: str, amount: float):
        """
        执行平仓操作
        
        Args:
            coin (str): 平仓币种
            amount (float): 平仓数量
        """
        # 获取当前持仓
        portfolio = self.db.get_portfolio(self.model_id)
        position = portfolio.get(coin, {'quantity': 0, 'avg_price': 0})
        current_quantity = position['quantity']
        avg_price = position['avg_price']
        
        # 检查持仓数量
        if current_quantity <= 0:
            print(f"没有 {coin} 持仓，无法平仓")
            return
        
        # 限制平仓数量不超过持仓数量
        close_amount = min(amount, current_quantity) if amount > 0 else current_quantity
        
        # 获取当前价格
        price_data = self.market_fetcher.get_current_price(coin)
        if not price_data:
            print(f"无法获取 {coin} 当前价格，无法平仓")
            return
        
        current_price = price_data['price']
        
        # 计算毛利润
        gross_profit = (current_price - avg_price) * close_amount
        
        # 计算交易费用（卖出部分）
        fee = (close_amount * current_price) * self.trade_fee_rate
        
        # 计算净利润
        net_profit = gross_profit - fee
        
        # 更新现金余额
        cash_balance = portfolio.get('cash', 0)
        new_cash_balance = cash_balance + (close_amount * current_price) - fee
        self.db.update_portfolio(self.model_id, 'cash', new_cash_balance)
        
        # 更新币种持仓
        new_quantity = current_quantity - close_amount
        if new_quantity <= 0:
            # 完全平仓，删除该币种持仓
            self.db.delete_position(self.model_id, coin)
        else:
            # 部分平仓，更新持仓数量
            self.db.update_portfolio(self.model_id, coin, new_quantity, avg_price)
        
        # 记录交易
        self.db.add_trade(self.model_id, coin, 'close', close_amount, current_price, fee, net_profit)
        
        print(f"成功平仓 {close_amount} {coin}，价格 ${current_price:.4f}，净利润 ${net_profit:.4f}")

# 实例化交易引擎（实际使用时会传入真实参数）
# trading_engine = TradingEngine(model_id, db, market_fetcher, ai_trader)
