package com.example.eurekaproducer.request;
/*
* Req8001: 查询交易所下所有期货代码
* Added by ZhangWH  2022.01.20
* */

public class Req8001 {
    /*
    * 交易所代码
    * */
    private String exchange;

    public String getExchange() {
        return exchange;
    }

    public void setExchange(String exchange) {
        this.exchange = exchange;
    }
}

