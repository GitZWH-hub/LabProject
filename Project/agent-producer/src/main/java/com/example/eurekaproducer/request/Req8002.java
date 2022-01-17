package com.example.eurekaproducer.request;


/*
    Req8001: Req pull data from TuShare
 */

public class Req8002 {

    private String type;

    private String exchange;

    private String start;

    private String end;

    public String getType() {
        return type;
    }

    public String getExchange() {
        return exchange;
    }

    public String getStart() {
        return start;
    }

    public String getEnd() {
        return end;
    }

    public void setType(String type) {
        this.type = type;
    }

    public void setExchange(String fut) { this.exchange = fut; }

    public void setStart(String start) {
        this.start = start;
    }

    public void setEnd(String end) {
        this.end = end;
    }

}

