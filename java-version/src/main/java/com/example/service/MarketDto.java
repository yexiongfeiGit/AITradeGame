package com.example.service;

import lombok.Data;

public class MarketDto {

    @Data
    public static class Market24hData {

        /** 当前价格 */
        private double price;
        
        /** 24小时价格变化百分比 */
        private double price_change_percent;
        
        /** 24小时交易量 */
        private double volume;
        
        /** 24小时最高价格 */
        private double high_price;
        
        /** 24小时最低价格 */
        private double low_price;

        // marketData.put("symbol", coin);
        // marketData.put("price", Double.parseDouble(data.getLastPrice()));
        // marketData.put("price_change_percent",
        // Double.parseDouble(data.getPriceChangePercent()));
        // marketData.put("volume", Double.parseDouble(data.getVolume()));
        // marketData.put("high_price", Double.parseDouble(data.getHighPrice()));
        // marketData.put("low_price", Double.parseDouble(data.getLowPrice()));
    }
}
