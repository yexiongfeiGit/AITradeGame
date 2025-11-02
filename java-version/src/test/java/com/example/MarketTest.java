package com.example;

import java.util.Map;

import com.alibaba.fastjson.JSON;
import com.example.service.MarketDataService;

public class MarketTest {
    public static MarketDataService marketDataService = new MarketDataService();

    public static void getMarketData() {
        Map<String, Object> marketData = marketDataService.getMarketData("BTC");
        System.out.println(JSON.toJSONString(marketData, true));
    }

    public static void main(String[] args) {
        getMarketData();
    }
}
