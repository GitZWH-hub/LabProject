package com.naah.bullet.request;


public class Req8102 {
//    交易日
    private String tradingDay;
//    合约代码
    private String instrumentID;
//    最新价
    private float LastPrice;
//    上次结算价
    private float PreSettlementPrice;
//    昨收盘
    private float PreClosePrice;
//    今开盘
    private float OpenPrice;
//    最高价
    private float HighestPrice;
//    最低价
    private float LowestPrice;
//    数量
    private int Volume;
//    今收盘
    private float ClosePrice;
//    本次结算价
    private float SettlementPrice;
//    涨停板价
    private float UpperLimitPrice;
//    跌停板价
    private float LowerLimitPrice;
//    申买价1
    private float BidPrice1;
//    申买量1
    private int BidVolume1;
//    申卖价1
    private float AskPrice1;
//    申卖量1
    private float AskVolume1;
    //    申买价2
    private float BidPrice2;
    //    申买量2
    private int BidVolume2;
    //    申卖价2
    private float AskPrice2;
    //    申卖量2
    private float AskVolume2;
    //    申买价3
    private float BidPrice3;
    //    申买量3
    private int BidVolume3;
    //    申卖价3
    private float AskPrice3;
    //    申卖量3
    private float AskVolume3;
    //    申买价4
    private float BidPrice4;
    //    申买量4
    private int BidVolume4;
    //    申卖价4
    private float AskPrice4;
    //    申卖量4
    private float AskVolume4;
    //    申买价5
    private float BidPrice5;
    //    申买量5
    private int BidVolume5;
    //    申卖价5
    private float AskPrice5;
    //    申卖量5
    private float AskVolume5;

//    当日均价
    private float AveragePrice;

    public String getTradingDay() {
        return this.tradingDay;
    }

    public String getInstrumentID() {
        return this.instrumentID;
    }

    public float getClosePrice() {
        return this.ClosePrice;
    }

    public float getHighestPrice() {
        return this.HighestPrice;
    }

    public float getLastPrice() {
        return this.LastPrice;
    }

    public float getLowerLimitPrice() {
        return this.LowerLimitPrice;
    }

    public float getLowestPrice() {
        return this.LowestPrice;
    }

    public float getOpenPrice() {
        return this.OpenPrice;
    }

    public float getPreClosePrice() {
        return this.PreClosePrice;
    }

    public float getPreSettlementPrice() {
        return this.PreSettlementPrice;
    }

    public float getSettlementPrice() {
        return this.SettlementPrice;
    }

    public float getBidPrice1() {
        return this.BidPrice1;
    }

    public int getVolume() {
        return this.Volume;
    }

    public float getUpperLimitPrice() {
        return this.UpperLimitPrice;
    }

    public int getBidVolume1() {
        return this.BidVolume1;
    }

    public float getAskVolume1() {
        return this.AskVolume1;
    }

    public float getAveragePrice() {
        return this.AveragePrice;
    }
    public float getAskPrice1() {
        return this.AskPrice1;
    }

    public void setLastPrice(float lastPrice) {
        this.LastPrice = lastPrice;
    }

    public void setBidVolume1(int bidVolume1) {
        this.BidVolume1 = bidVolume1;
    }

    public void setLowestPrice(float lowestPrice) {
        this.LowestPrice = lowestPrice;
    }

    public void setTradingDay(String tradingDay) {
        this.tradingDay = tradingDay;
    }

    public void setInstrumentID(String instrumentID) {
        this.instrumentID = instrumentID;
    }

    public void setAskPrice1(float askPrice1) {
        this.AskPrice1 = askPrice1;
    }

    public void setLowerLimitPrice(float lowerLimitPrice) {
        this.LowerLimitPrice = lowerLimitPrice;
    }

    public void setOpenPrice(float openPrice) {
        this.OpenPrice = openPrice;
    }


    public void setPreClosePrice(float preClosePrice) {
        this.PreClosePrice = preClosePrice;
    }

    public void setPreSettlementPrice(float preSettlementPrice) {
        this.PreSettlementPrice = preSettlementPrice;
    }

    public void setSettlementPrice(float settlementPrice) {
        this.SettlementPrice = settlementPrice;
    }

    public void setAskVolume1(float askVolume1) {
        this.AskVolume1 = askVolume1;
    }

    public void setUpperLimitPrice(float upperLimitPrice) {
        this.UpperLimitPrice = upperLimitPrice;
    }

    public void setVolume(int volume) {
        this.Volume = volume;
    }

    public void setAveragePrice(float averagePrice) {
        this.AveragePrice = averagePrice;
    }
    public void setClosePrice(float closePrice) {
        this.ClosePrice = closePrice;
    }

    public void setBidPrice1(float bidPrice1) {
        this.BidPrice1 = bidPrice1;
    }

    public void setHighestPrice(float highestPrice) {
        this.HighestPrice = highestPrice;
    }

    public float getAskPrice2() {
        return this.AskPrice2;
    }

    public float getAskPrice3() {
        return this.AskPrice3;
    }

    public float getAskPrice4() {
        return this.AskPrice4;
    }

    public float getAskPrice5() {
        return this.AskPrice5;
    }

    public float getAskVolume2() {
        return this.AskVolume2;
    }

    public float getAskVolume3() {
        return this.AskVolume3;
    }

    public float getAskVolume4() {
        return this.AskVolume4;
    }

    public float getAskVolume5() {
        return this.AskVolume5;
    }

    public float getBidPrice2() {
        return this.BidPrice2;
    }

    public float getBidPrice3() {
        return this.BidPrice3;
    }

    public float getBidPrice4() {
        return this.BidPrice4;
    }

    public float getBidPrice5() {
        return this.BidPrice5;
    }

    public int getBidVolume2() {
        return this.BidVolume2;
    }

    public int getBidVolume3() {
        return this.BidVolume3;
    }

    public int getBidVolume4() {
        return this.BidVolume4;
    }

    public int getBidVolume5() {
        return this.BidVolume5;
    }

    public void setAskPrice2(float askPrice2) {
        this.AskPrice2 = askPrice2;
    }

    public void setAskPrice3(float askPrice3) {
        this.AskPrice3 = askPrice3;
    }

    public void setAskPrice4(float askPrice4) {
        this.AskPrice4 = askPrice4;
    }

    public void setAskPrice5(float askPrice5) {
        this.AskPrice5 = askPrice5;
    }

    public void setAskVolume2(float askVolume2) {
        this.AskVolume2 = askVolume2;
    }

    public void setAskVolume3(float askVolume3) {
        this.AskVolume3 = askVolume3;
    }

    public void setAskVolume4(float askVolume4) {
        this.AskVolume4 = askVolume4;
    }

    public void setAskVolume5(float askVolume5) {
        this.AskVolume5 = askVolume5;
    }

    public void setBidPrice2(float bidPrice2) {
        this.BidPrice2 = bidPrice2;
    }

    public void setBidPrice3(float bidPrice3) {
        this.BidPrice3 = bidPrice3;
    }

    public void setBidPrice4(float bidPrice4) {
        this.BidPrice4 = bidPrice4;
    }

    public void setBidPrice5(float bidPrice5) {
        this.BidPrice5 = bidPrice5;
    }

    public void setBidVolume2(int bidVolume2) {
        this.BidVolume2 = bidVolume2;
    }

    public void setBidVolume3(int bidVolume3) {
        this.BidVolume3 = bidVolume3;
    }

    public void setBidVolume4(int bidVolume4) {
        this.BidVolume4 = bidVolume4;
    }

    public void setBidVolume5(int bidVolume5) {
        this.BidVolume5 = bidVolume5;
    }
    //    昨持仓量
    private int PreOpenInterest;
//    成交金额
    private long Turnover;
//    持仓量
    private int OpenInterest;
//    昨虚实度
    private float PreDelta;
//    今虚实度
    private float CurrDelta;
//    最后修改时间
    private String UpdateTime;
//    最后修改毫秒
    private int UpdateMillisec;
//    业务日期
    private String ActionDay;

    public float getCurrDelta() {
        return this.CurrDelta;
    }

    public float getPreDelta() {
        return this.PreDelta;
    }

    public int getOpenInterest() {
        return this.OpenInterest;
    }

    public int getPreOpenInterest() {
        return this.PreOpenInterest;
    }

    public long getTurnover() {
        return this.Turnover;
    }

    public int getUpdateMillisec() {
        return this.UpdateMillisec;
    }

    public void setPreOpenInterest(int preOpenInterest) {
        this.PreOpenInterest = preOpenInterest;
    }

    public void setTurnover(long turnover) {
        this.Turnover = turnover;
    }

    public String getActionDay() {
        return this.ActionDay;
    }

    public String getUpdateTime() {
        return this.UpdateTime;
    }

    public void setOpenInterest(int openInterest) {
        this.OpenInterest = openInterest;
    }

    public void setCurrDelta(float currDelta) {
        this.CurrDelta = currDelta;
    }

    public void setPreDelta(float preDelta) {
        this.PreDelta = preDelta;
    }

    public void setUpdateMillisec(int updateMillisec) {
        this.UpdateMillisec = updateMillisec;
    }

    public void setActionDay(String actionDay) {
        this.ActionDay = actionDay;
    }

    public void setUpdateTime(String updateTime) {
        this.UpdateTime = updateTime;
    }

}
