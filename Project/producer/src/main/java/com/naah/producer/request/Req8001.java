package com.naah.producer.request;


/*
    Req8001: k-line request
 */

public class Req8001 {
    private String fut;

    private String futEnd;

    private String start;

    private String end;

    public String getFut() { return fut; }

    public String getFutEnd() { return futEnd;}

    public String getStart() { return start; }

    public String getEnd() { return end; }

    public void setFut(String fut) { this.fut = fut; }

    public void setFutEnd(String futEnd) { this.futEnd = futEnd;}

    public void setEnd(String end) { this.end = end; }

    public void setStart(String start) { this.start = start; }

}

