

from market_data import MarketDataFetcher

    
def test_get_current_price():
    """简单测试get_current_price方法，只打印返回值"""
    print("------===-------")
    market_data_fetcher = MarketDataFetcher()
    
    # 测试获取BTC价格
    result = market_data_fetcher.get_current_price('BTC')
    print("BTC Market Data:", result)
    
    # 测试获取ETH价格
    result = market_data_fetcher.get_current_price('ETH')
    print("ETH Market Data:", result)
    
    # 测试获取一个无效的币种
    result = market_data_fetcher.get_current_price('INVALIDCOIN')
    print("Invalid Coin Data:", result)

def test_get_historical_prices():
    """简单测试get_historical_prices方法，只打印返回值"""
    print("------===-------")
    market_data_fetcher = MarketDataFetcher()
    
    # 测试获取BTC历史价格
    result = market_data_fetcher.get_historical_prices('bitcoin', 10)
    print("BTC Historical Prices:", result)
    
    # 测试获取ETH历史价格
    result = market_data_fetcher.get_historical_prices('ethereum', 10)
    print("ETH Historical Prices:", result)
    
    # 测试获取一个无效的币种
    result = market_data_fetcher.get_historical_prices('INVALIDCOIN', 1)
    print("Invalid Coin Historical Prices:", result)

def test_get_coin_data_with_indicators():
    """简单测试get_coin_data_with_indicators方法，只打印返回值"""
    print("------5555-------")
    market_data_fetcher = MarketDataFetcher()
    
    # 测试获取BTC数据及指标
    result = market_data_fetcher.get_coin_data_with_indicators('bitcoin')
    print("BTC Data with Indicators:", result)


if __name__ == '__main__':
    test_get_coin_data_with_indicators()
       