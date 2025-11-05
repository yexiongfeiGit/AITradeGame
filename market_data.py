"""
市场数据获取模块

该模块负责从各种API获取加密货币市场数据，包括：
1. 实时价格和24小时变化率
2. 详细市场数据（市值、流通供应量等）
3. 历史价格数据
4. 技术指标计算（SMA、RSI等）

支持多个数据源，并实现了缓存机制以减少API调用次数。
"""

import requests
import time
import json
from typing import Dict, List, Optional, Tuple

class MarketDataFetcher:
    """
    市场数据获取器类
    
    该类封装了从Binance和CoinGecko API获取市场数据的方法，
    并提供了缓存机制和技术指标计算功能。
    """
    
    def __init__(self, cache_duration=5, api_url="https://api.binance.com"):
        """
        初始化市场数据获取器
        
        设置API端点、缓存变量和缓存过期时间。
        
        Args:
            cache_duration (int): 缓存持续时间（秒），默认为5秒
            api_url (str): Binance API的基础URL，默认为"https://api.binance.com"
        """
        # Binance API端点
        self.binance_base_url = api_url
        
        # CoinGecko API端点
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
        
        # 缓存变量
        self._cache = {}
        self._cache_expiry = {}
        self.cache_duration = cache_duration  # 缓存持续时间（秒）
    
    def _is_cache_valid(self, key: str) -> bool:
        """
        检查缓存是否有效
        
        Args:
            key (str): 缓存键
            
        Returns:
            bool: 如果缓存有效返回True，否则返回False
        """
        if key not in self._cache_expiry:
            return False
        return time.time() < self._cache_expiry[key]
    
    def _set_cache(self, key: str, data):
        """
        设置缓存数据
        
        Args:
            key (str): 缓存键
            data: 要缓存的数据
        """
        self._cache[key] = data
        self._cache_expiry[key] = time.time() + self.cache_duration
    
    def _get_cache(self, key: str):
        """
        获取缓存数据
        
        Args:
            key (str): 缓存键
            
        Returns:
            缓存的数据，如果缓存无效或不存在则返回None
        """
        if self._is_cache_valid(key):
            return self._cache[key]
        return None
    
    def get_current_price(self, coin: str) -> Optional[Dict]:
        """
        获取指定币种的当前价格和24小时变化率
        
        首先尝试从Binance获取数据，如果失败则降级到CoinGecko。
        
        Args:
            coin (str): 币种符号（如BTC、ETH等）
            
        Returns:
            Optional[Dict]: 包含价格和变化率的字典，如果获取失败则返回None
        """
        # 尝试从缓存获取数据
        cache_key = f"price_{coin}"
        cached_data = self._get_cache(cache_key)
        if cached_data:
            return cached_data
        
        # 构建币种对（使用USDT作为计价货币）
        symbol = f"{coin}USDT"
        
        try:
            # 首先尝试从Binance获取数据
            url = f"{self.binance_base_url}/api/v3/ticker/24hr"
            params = {"symbol": symbol}
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                price_info = {
                    "coin": coin,
                    "price": float(data["lastPrice"]),
                    "change_24h": float(data["priceChangePercent"])
                }
                # 缓存数据
                self._set_cache(cache_key, price_info)
                return price_info
        except Exception as e:
            print(f"从Binance获取{coin}价格失败: {e}")
        
        try:
            # 如果Binance失败，尝试从CoinGecko获取
            url = f"{self.coingecko_base_url}/simple/price"
            params = {
                "ids": coin.lower(),
                "vs_currencies": "usd",
                "include_24hr_change": "true"
            }
            response = requests.get(url, params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                coin_id = coin.lower()
                if coin_id in data and "usd" in data[coin_id]:
                    price_info = {
                        "coin": coin,
                        "price": float(data[coin_id]["usd"]),
                        "change_24h": float(data[coin_id].get("usd_24h_change", 0))
                    }
                    # 缓存数据
                    self._set_cache(cache_key, price_info)
                    return price_info
        except Exception as e:
            print(f"从CoinGecko获取{coin}价格失败: {e}")
        
        # 如果所有方法都失败，返回None
        return None
    
    def get_market_data(self, coin: str) -> Optional[Dict]:
        """
        获取指定币种的详细市场数据
        
        Args:
            coin (str): 币种符号（如BTC、ETH等）
            
        Returns:
            Optional[Dict]: 包含详细市场数据的字典，如果获取失败则返回None
        """
        # 尝试从缓存获取数据
        cache_key = f"market_{coin}"
        cached_data = self._get_cache(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # 从CoinGecko获取详细市场数据
            url = f"{self.coingecko_base_url}/coins/{coin.lower()}"
            params = {
                "localization": "false",
                "tickers": "false",
                "market_data": "true",
                "community_data": "false",
                "developer_data": "false",
                "sparkline": "false"
            }
            response = requests.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                market_info = {
                    "coin": coin,
                    "price": float(data["market_data"]["current_price"]["usd"]),
                    "market_cap": data["market_data"]["market_cap"]["usd"],
                    "market_cap_rank": data["market_data"]["market_cap_rank"],
                    "volume_24h": data["market_data"]["total_volume"]["usd"],
                    "high_24h": data["market_data"]["high_24h"]["usd"],
                    "low_24h": data["market_data"]["low_24h"]["usd"],
                    "price_change_24h": data["market_data"]["price_change_24h"],
                    "price_change_percentage_24h": data["market_data"]["price_change_percentage_24h"],
                    "circulating_supply": data["market_data"]["circulating_supply"],
                    "total_supply": data["market_data"]["total_supply"],
                    "max_supply": data["market_data"]["max_supply"]
                }
                # 缓存数据
                self._set_cache(cache_key, market_info)
                return market_info
        except Exception as e:
            print(f"从CoinGecko获取{coin}市场数据失败: {e}")
        
        # 如果获取失败，返回None
        return None
    
    def get_historical_prices(self, coin: str, days: int = 7) -> Optional[List[Dict]]:
        """
        获取指定币种的历史价格数据
        
        Args:
            coin (str): 币种符号（如BTC、ETH等）
            days (int): 获取天数，默认为7天
            
        Returns:
            Optional[List[Dict]]: 历史价格数据列表，如果获取失败则返回None
        """
        # 尝试从缓存获取数据
        cache_key = f"history_{coin}_{days}"
        cached_data = self._get_cache(cache_key)
        if cached_data:
            return cached_data
        
        try:
           # https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=30&interval=daily
            # 从CoinGecko获取历史价格数据
            url = f"{self.coingecko_base_url}/coins/{coin.lower()}/market_chart"
            params = {
                "vs_currency": "usd",
                "days": days,
                "interval": "daily"
            }
            response = requests.get(url, params=params, timeout=10)
            # print(f"请求URL: {url}")
            # print(f"请求参数: {params}")
            # print(f"响应状态码: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                # 解析价格数据
                prices = []
                for point in data["prices"]:
                    prices.append({
                        "timestamp": point[0],
                        "price": point[1]
                    })
                # 缓存数据
                self._set_cache(cache_key, prices)
                return prices
        except Exception as e:
            print(f"从CoinGecko获取{coin}历史价格失败: {e}")
        
        # 如果获取失败，返回None
        return None
    
    def calculate_sma(self, prices: List[float], period: int = 7) -> Optional[float]:
        """
        计算简单移动平均线（SMA）
        
        Args:
            prices (List[float]): 价格列表
            period (int): 计算周期，默认为7
            
        Returns:
            Optional[float]: SMA值，如果数据不足则返回None
        """
        if len(prices) < period:
            return None
        
        # 计算最近period个价格的平均值
        sma = sum(prices[-period:]) / period
        return sma
    
    def calculate_rsi(self, prices: List[float], period: int = 14) -> Optional[float]:
        """
        计算相对强弱指数（RSI）
        
        Args:
            prices (List[float]): 价格列表
            period (int): 计算周期，默认为14
            
        Returns:
            Optional[float]: RSI值（0-100），如果数据不足则返回None
        """
        if len(prices) < period + 1:
            return None
        
        # 计算价格变化
        deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
        
        # 分离上涨和下跌
        gains = [delta if delta > 0 else 0 for delta in deltas]
        losses = [-delta if delta < 0 else 0 for delta in deltas]
        
        # 计算平均上涨和下跌
        avg_gain = sum(gains[-period:]) / period
        avg_loss = sum(losses[-period:]) / period
        
        # 如果没有下跌，RSI为100
        if avg_loss == 0:
            return 100.0
        
        # 计算RSI
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_change_7d(self, prices: List[float]) -> Optional[float]:
        """
        计算7日价格变化率
        
        Args:
            prices (List[float]): 价格列表
            
        Returns:
            Optional[float]: 7日价格变化率（百分比），如果数据不足则返回None
        """
        if len(prices) < 7:
            return None
        
        # 计算7日前的价格和当前价格
        price_7d_ago = prices[-7]
        current_price = prices[-1]
        
        # 计算变化率
        change = ((current_price - price_7d_ago) / price_7d_ago) * 100
        return change
    
    def get_coin_data_with_indicators(self, coin: str) -> Optional[Dict]:
        """
        获取币种数据及技术指标
        
        Args:
            coin (str): 币种符号
            
        Returns:
            Optional[Dict]: 包含价格数据和技术指标的字典，如果获取失败则返回None
        """
        # 获取当前价格
        price_data = self.get_current_price(coin)
        print(f"获取{coin}当前价格: {price_data}")
        if not price_data:
            return None
        
        # 获取历史价格（14天）
        historical_data = self.get_historical_prices(coin, 14)
        print(f"获取{coin}历史价格: {historical_data}")
        if not historical_data:
            return price_data
        
        # 提取价格列表
        prices = [point["price"] for point in historical_data]
        print(f"提取{coin}历史价格列表: {prices}")
        
        # 计算技术指标
        sma_7 = self.calculate_sma(prices, 7)
        sma_14 = self.calculate_sma(prices, 14)
        rsi = self.calculate_rsi(prices, 14)
        change_7d = self.calculate_change_7d(prices)
        print(f"计算{coin}7日SMA: {sma_7}")
        print(f"计算{coin}14日SMA: {sma_14}")
        print(f"计算{coin}14日RSI: {rsi}")
        
        # 合并所有数据
        result = {
            **price_data,
            "sma_7": sma_7,
            "sma_14": sma_14,
            "rsi": rsi,
            "change_7d": change_7d
        }
        print(f"合并{coin}数据及指标: {result}")
        return result

    def get_prices(self) -> Dict[str, Dict]:
        """
        获取所有交易币种的当前价格信息
        
        从配置中获取交易币种列表，然后为每个币种获取当前价格和24小时变化率。
        
        Returns:
            Dict[str, Dict]: 以币种为键，价格信息为值的字典
        """
        from config import Config
        
        prices = {}
        for coin in Config.COINS:
            try:
                price_info = self.get_current_price(coin)
                if price_info:
                    # 只保留需要的字段
                    prices[coin] = {
                        "price": price_info["price"],
                        "change_24h": price_info["change_24h"]
                    }
                else:
                    # 如果获取失败，添加默认值
                    prices[coin] = {
                        "price": 0,
                        "change_24h": 0
                    }
            except Exception as e:
                print(f"获取{coin}价格时出错: {e}")
                # 出错时添加默认值
                prices[coin] = {
                    "price": 0,
                    "change_24h": 0
                }
        
        return prices

# 创建全局市场数据获取器实例
market_fetcher = MarketDataFetcher()

