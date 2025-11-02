"""
AI Trader Module - 使用大语言模型进行加密货币交易决策

该模块实现了基于大语言模型的AI交易器，能够根据市场数据、投资组合状态和账户信息
生成交易决策。它通过构建提示词、调用LLM并解析响应来完成整个决策流程。
"""

import json
from typing import Dict
from openai import OpenAI, APIConnectionError, APIError

class AITrader:
    """
    AI交易器类
    
    该类负责构建交易决策提示词、调用大语言模型并解析模型输出，
    最终生成具体的交易决策。
    """
    
    def __init__(self, api_key: str, api_url: str, model_name: str):
        """
        初始化AI交易器
        
        Args:
            api_key (str): LLM API密钥
            api_url (str): LLM API地址
            model_name (str): 使用的模型名称
        """
        self.api_key = api_key
        self.api_url = api_url
        self.model_name = model_name
    
    def make_decision(self, market_state: Dict, portfolio: Dict, 
                     account_info: Dict) -> Dict:
        """
        生成交易决策
        
        该方法是AI交易器的核心接口，负责整个决策流程：
        1. 构建提示词
        2. 调用大语言模型
        3. 解析模型响应
        
        Args:
            market_state (Dict): 市场状态数据，包含各币种的当前价格和指标
            portfolio (Dict): 投资组合信息，包含持仓和现金等
            account_info (Dict): 账户信息，包含初始资金和总收益等
            
        Returns:
            Dict: 交易决策结果，包含各币种的交易信号和参数
        """
        # 构建提示词
        prompt = self._build_prompt(market_state, portfolio, account_info)
        
        # 调用大语言模型
        response = self._call_llm(prompt)
        
        # 解析模型响应
        decisions = self._parse_response(response)
        
        return decisions
    
    def _build_prompt(self, market_state: Dict, portfolio: Dict, 
                     account_info: Dict) -> str:
        """
        构建发送给大语言模型的提示词
        
        提示词包含市场数据、账户状态、持仓信息和交易规则，指导模型做出合理的交易决策。
        
        Args:
            market_state (Dict): 市场状态数据
            portfolio (Dict): 投资组合信息
            account_info (Dict): 账户信息
            
        Returns:
            str: 构建好的提示词字符串
        """
        # 提示词开头部分，说明角色和任务
        prompt = f"""You are a professional cryptocurrency trader. Analyze the market and make trading decisions.

MARKET DATA:
"""
        # 添加各币种的市场数据
        for coin, data in market_state.items():
            prompt += f"{coin}: ${data['price']:.2f} ({data['change_24h']:+.2f}%)\n"
            # 如果有技术指标数据，则添加技术指标
            if 'indicators' in data and data['indicators']:
                indicators = data['indicators']
                prompt += f"  SMA7: ${indicators.get('sma_7', 0):.2f}, SMA14: ${indicators.get('sma_14', 0):.2f}, RSI: {indicators.get('rsi_14', 0):.1f}\n"
        
        # 添加账户状态信息
        prompt += f"""
ACCOUNT STATUS:
- Initial Capital: ${account_info['initial_capital']:.2f}
- Total Value: ${portfolio['total_value']:.2f}
- Cash: ${portfolio['cash']:.2f}
- Total Return: {account_info['total_return']:.2f}%

CURRENT POSITIONS:
"""
        # 添加当前持仓信息
        if portfolio['positions']:
            for pos in portfolio['positions']:
                prompt += f"- {pos['coin']} {pos['side']}: {pos['quantity']:.4f} @ ${pos['avg_price']:.2f} ({pos['leverage']}x)\n"
        else:
            prompt += "None\n"
        
        # 添加交易规则说明
        prompt += """
TRADING RULES:
1. Signals: buy_to_enter (long), sell_to_enter (short), close_position, hold
2. Risk Management:
   - Max 3 positions
   - Risk 1-5% per trade
   - Use appropriate leverage (1-20x)
3. Position Sizing:
   - Conservative: 1-2% risk
   - Moderate: 2-4% risk
   - Aggressive: 4-5% risk
4. Exit Strategy:
   - Close losing positions quickly
   - Let winners run
   - Use technical indicators

OUTPUT FORMAT (JSON only):
```json
{
  "COIN": {
    "signal": "buy_to_enter|sell_to_enter|hold|close_position",
    "quantity": 0.5,
    "leverage": 10,
    "profit_target": 45000.0,
    "stop_loss": 42000.0,
    "confidence": 0.75,
    "justification": "Brief reason"
  }
}
```

Analyze and output JSON only.
"""
        
        return prompt
    
    def _call_llm(self, prompt: str) -> str:
        """
        调用大语言模型API
        
        该方法处理与LLM API的通信，包括构建客户端、发送请求和处理异常。
        
        Args:
            prompt (str): 发送给模型的提示词
            
        Returns:
            str: 模型的响应内容
            
        Raises:
            Exception: 当API调用失败时抛出异常
        """
        try:
            # 处理API URL，确保以/v1结尾
            base_url = self.api_url.rstrip('/')
            if not base_url.endswith('/v1'):
                if '/v1' in base_url:
                    base_url = base_url.split('/v1')[0] + '/v1'
                else:
                    base_url = base_url + '/v1'
            
            # 创建OpenAI客户端
            client = OpenAI(
                api_key=self.api_key,
                base_url=base_url
            )
            
            # 发送聊天完成请求
            response = client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {
                        "role": "system",
                        "content": "You are a professional cryptocurrency trader. Output JSON format only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            
            return response.choices[0].message.content
            
        # 处理API连接错误
        except APIConnectionError as e:
            error_msg = f"API connection failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            raise Exception(error_msg)
        # 处理API错误
        except APIError as e:
            error_msg = f"API error ({e.status_code}): {e.message}"
            print(f"[ERROR] {error_msg}")
            raise Exception(error_msg)
        # 处理其他异常
        except Exception as e:
            error_msg = f"LLM call failed: {str(e)}"
            print(f"[ERROR] {error_msg}")
            import traceback
            print(traceback.format_exc())
            raise Exception(error_msg)
    
    def _parse_response(self, response: str) -> Dict:
        """
        解析模型响应
        
        从模型的响应中提取JSON格式的交易决策。
        
        Args:
            response (str): 模型的原始响应字符串
            
        Returns:
            Dict: 解析后的交易决策字典
        """
        response = response.strip()
        
        # 提取JSON内容（处理可能的代码块标记）
        if '```json' in response:
            response = response.split('```json')[1].split('```')[0]
        elif '```' in response:
            response = response.split('```')[1].split('```')[0]
        
        try:
            # 解析JSON
            decisions = json.loads(response.strip())
            return decisions
        except json.JSONDecodeError as e:
            print(f"[ERROR] JSON parse failed: {e}")
            print(f"[DATA] Response:\n{response}")
            return {}
