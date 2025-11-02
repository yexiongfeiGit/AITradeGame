package com.example;

import java.util.Arrays;
import java.util.Map;
import java.util.List;

import com.alibaba.fastjson.JSON;
import com.example.service.MarketDataService;
import com.example.service.MarketDto.Market24hData;

public class MarketTest {
    public static MarketDataService marketDataService = new MarketDataService();

    private static final List<String> SUPPORTED_COINS = Arrays.asList(
            "BTC", "ETH", "BNB", "SOL", "XRP", "ADA", "DOGE", "DOT",
            "AVAX", "LINK", "MATIC", "UNI", "LTC", "ATOM", "ETC");

    public static void getMarketData() {
        Map<String, Object> marketData = marketDataService.getMarketData("BTC");
        System.out.println(JSON.toJSONString(marketData, true));
    }

    public static void getCurrentPrice() {
        Map<String, Double> currentPrices = marketDataService.getCurrentPrices(SUPPORTED_COINS.toArray(new String[0]));
        System.out.println(JSON.toJSONString(currentPrices, true));
    }

    public static void getMarket24hData() {

    }

    public static void main(String[] args) {
        getCurrentPrice();
        // {'coin': 'BTC', 'price': 110930.57, 'change_24h': 0.774}
        // 30101128306, 'price_change_24h': 0.65292, 'price_change_7d': -0.83803,
        // 'high_24h': 110985, 'low_24h': 109713}
    }
}
