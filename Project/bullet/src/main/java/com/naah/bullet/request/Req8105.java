package com.naah.bullet.request;



public class Req8105 {
    private String fut;

    private String start;

    private String end;

    private int longT;

    private int shortT;

    private long cash;

    public void setStart(String start) {
        this.start = start;
    }

    public void setEnd(String end) {
        this.end = end;
    }

    public String getStart() {
        return start;
    }

    public String getEnd() {
        return end;
    }

    public int getLongT() {
        return longT;
    }

    public int getShortT() {
        return shortT;
    }

    public long getCash() {
        return cash;
    }

    public String getFut() {
        return fut;
    }

    public void setCash(long cash) {
        this.cash = cash;
    }

    public void setFut(String fut) {
        this.fut = fut;
    }

    public void setLongT(int longT) {
        this.longT = longT;
    }

    public void setShortT(int shortT) {
        this.shortT = shortT;
    }
}