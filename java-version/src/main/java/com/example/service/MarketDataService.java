package com.example.service;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.ResponseEntity;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestClientException;
import org.springframework.web.client.RestTemplate;

import java.util.HashMap;
import java.util.Map;
import java.util.concurrent.ConcurrentHashMap;

@Service
public class MarketDataService {

    private static final Logger logger = LoggerFactory.getLogger(MarketDataService.class);

    private final RestTemplate restTemplate = new RestTemplate();

    // 缓存价格数据
    private final Map<String, Double> priceCache = new ConcurrentHashMap<>();
    private final Map<String, Long> cacheTimestamps = new ConcurrentHashMap<>();
    private static final long CACHE_DURATION = 30000; // 30秒缓存

    // 符号映射
    private final Map<String, String> symbolMapping = new HashMap<>();

    public MarketDataService() {
        // 初始化符号映射
        symbolMapping.put("BTC", "BTCUSDT");
        symbolMapping.put("ETH", "ETHUSDT");
        symbolMapping.put("BNB", "BNBUSDT");
        symbolMapping.put("SOL", "SOLUSDT");
        symbolMapping.put("XRP", "XRPUSDT");
        symbolMapping.put("ADA", "ADAUSDT");
        symbolMapping.put("DOGE", "DOGEUSDT");
        symbolMapping.put("DOT", "DOTUSDT");
        symbolMapping.put("AVAX", "AVAXUSDT");
        symbolMapping.put("LINK", "LINKUSDT");
        symbolMapping.put("MATIC", "MATICUSDT");
        symbolMapping.put("UNI", "UNIUSDT");
        symbolMapping.put("LTC", "LTCUSDT");
        symbolMapping.put("ATOM", "ATOMUSDT");
        symbolMapping.put("ETC", "ETCUSDT");
    }

    /**
     * 获取当前价格
     */
    public Map<String, Double> getCurrentPrices(String[] coins) {
        Map<String, Double> prices = new HashMap<>();

        try {
            // 首先尝试从Binance获取价格
            prices = getPricesFromBinance(coins);
        } catch (Exception e) {
            logger.warn("Failed to get prices from Binance, trying CoinGecko as fallback: {}", e.getMessage());
            try {
                // 备用方案：从CoinGecko获取价格
                prices = getPricesFromCoinGecko(coins);
            } catch (Exception ex) {
                logger.error("Failed to get prices from CoinGecko: {}", ex.getMessage());
            }
        }

        return prices;
    }

    /**
     * 从Binance获取价格
     */
    private Map<String, Double> getPricesFromBinance(String[] coins) {
        Map<String, Double> prices = new HashMap<>();
        StringBuilder symbolsBuilder = new StringBuilder();

        // 构建符号字符串
        for (String coin : coins) {
            String symbol = symbolMapping.getOrDefault(coin, coin + "USDT");
            if (symbolsBuilder.length() > 0) {
                symbolsBuilder.append(",");
            }
            symbolsBuilder.append(symbol);
        }

        String url = "https://api.binance.com/api/v3/ticker/price?symbols=[" + symbolsBuilder.toString() + "]";

        try {
            ResponseEntity<BinancePriceResponse[]> response = restTemplate.getForEntity(
                    url.replace("[", "%5B").replace("]", "%5D"), BinancePriceResponse[].class);

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                for (BinancePriceResponse priceData : response.getBody()) {
                    String symbol = priceData.getSymbol();
                    // 反向查找币种名称
                    for (Map.Entry<String, String> entry : symbolMapping.entrySet()) {
                        if (entry.getValue().equals(symbol)) {
                            prices.put(entry.getKey(), Double.parseDouble(priceData.getPrice()));
                            break;
                        }
                    }
                }
            }
        } catch (RestClientException e) {
            logger.error("Error fetching prices from Binance: {}", e.getMessage());
            throw e;
        }

        return prices;
    }

    /**
     * 从CoinGecko获取价格（备用方案）
     */
    private Map<String, Double> getPricesFromCoinGecko(String[] coins) {
        Map<String, Double> prices = new HashMap<>();
        StringBuilder idsBuilder = new StringBuilder();

        // 构建ID字符串
        Map<String, String> coinIds = new HashMap<>();
        coinIds.put("BTC", "bitcoin");
        coinIds.put("ETH", "ethereum");
        coinIds.put("BNB", "binancecoin");
        coinIds.put("SOL", "solana");
        coinIds.put("XRP", "ripple");
        coinIds.put("ADA", "cardano");
        coinIds.put("DOGE", "dogecoin");
        coinIds.put("DOT", "polkadot");
        coinIds.put("AVAX", "avalanche-2");
        coinIds.put("LINK", "chainlink");
        coinIds.put("MATIC", "matic-network");
        coinIds.put("UNI", "uniswap");
        coinIds.put("LTC", "litecoin");
        coinIds.put("ATOM", "cosmos");
        coinIds.put("ETC", "ethereum-classic");

        for (String coin : coins) {
            String id = coinIds.get(coin);
            if (id != null) {
                if (idsBuilder.length() > 0) {
                    idsBuilder.append(",");
                }
                idsBuilder.append(id);
            }
        }

        String url = "https://api.coingecko.com/api/v3/simple/price?ids=" + idsBuilder.toString()
                + "&vs_currencies=usd";

        try {
            ResponseEntity<Map> response = restTemplate.getForEntity(url, Map.class);

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                Map<String, Object> responseBody = response.getBody();

                for (Map.Entry<String, String> entry : coinIds.entrySet()) {
                    String coin = entry.getKey();
                    String id = entry.getValue();

                    if (responseBody.containsKey(id)) {
                        Map<String, Object> coinData = (Map<String, Object>) responseBody.get(id);
                        if (coinData.containsKey("usd")) {
                            prices.put(coin, ((Number) coinData.get("usd")).doubleValue());
                        }
                    }
                }
            }
        } catch (RestClientException e) {
            logger.error("Error fetching prices from CoinGecko: {}", e.getMessage());
            throw e;
        }

        return prices;
    }

    /**
     * 获取市场数据
     */
    public Map<String, Object> getMarketData(String coin) {
        Map<String, Object> marketData = new HashMap<>();

        try {
            String symbol = symbolMapping.getOrDefault(coin, coin + "USDT");
            String url = "https://api.binance.com/api/v3/ticker/24hr?symbol=" + symbol;

            ResponseEntity<BinanceMarketDataResponse> response = restTemplate.getForEntity(url,
                    BinanceMarketDataResponse.class);

            if (response.getStatusCode().is2xxSuccessful() && response.getBody() != null) {
                BinanceMarketDataResponse data = response.getBody();
                marketData.put("symbol", coin);
                marketData.put("price", Double.parseDouble(data.getLastPrice()));
                marketData.put("price_change_percent", Double.parseDouble(data.getPriceChangePercent()));
                marketData.put("volume", Double.parseDouble(data.getVolume()));
                marketData.put("high_price", Double.parseDouble(data.getHighPrice()));
                marketData.put("low_price", Double.parseDouble(data.getLowPrice()));
            }
        } catch (Exception e) {
            logger.error("Error fetching market data for {}: {}", coin, e.getMessage());
        }

        return marketData;
    }

    /**
     * 计算技术指标
     */
    public Map<String, Object> calculateTechnicalIndicators(String coin) {
        Map<String, Object> indicators = new HashMap<>();

        try {
            // 这里简化实现，实际应该获取历史数据进行计算
            Map<String, Object> marketData = getMarketData(coin);

            if (!marketData.isEmpty()) {
                double price = (Double) marketData.get("price");

                // 简化的SMA计算（这里只是示例）
                double sma = price; // 实际应基于历史数据

                // 简化的RSI计算（这里只是示例）
                double rsi = 50.0; // 实际应基于历史价格变化

                indicators.put("SMA_20", sma);
                indicators.put("RSI_14", rsi);
            }
        } catch (Exception e) {
            logger.error("Error calculating technical indicators for {}: {}", coin, e.getMessage());
        }

        return indicators;
    }

    // Binance价格响应内部类
    public static class BinancePriceResponse {
        private String symbol;
        private String price;

        // Getters and setters
        public String getSymbol() {
            return symbol;
        }

        public void setSymbol(String symbol) {
            this.symbol = symbol;
        }

        public String getPrice() {
            return price;
        }

        public void setPrice(String price) {
            this.price = price;
        }
    }

    // Binance市场数据响应内部类
    public static class BinanceMarketDataResponse {
        private String lastPrice;
        private String priceChangePercent;
        private String volume;
        private String highPrice;
        private String lowPrice;

        // Getters and setters
        public String getLastPrice() {
            return lastPrice;
        }

        public void setLastPrice(String lastPrice) {
            this.lastPrice = lastPrice;
        }

        public String getPriceChangePercent() {
            return priceChangePercent;
        }

        public void setPriceChangePercent(String priceChangePercent) {
            this.priceChangePercent = priceChangePercent;
        }

        public String getVolume() {
            return volume;
        }

        public void setVolume(String volume) {
            this.volume = volume;
        }

        public String getHighPrice() {
            return highPrice;
        }

        public void setHighPrice(String highPrice) {
            this.highPrice = highPrice;
        }

        public String getLowPrice() {
            return lowPrice;
        }

        public void setLowPrice(String lowPrice) {
            this.lowPrice = lowPrice;
        }
    }
}