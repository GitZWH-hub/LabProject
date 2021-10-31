#!/usr/bin/env python
# -*-coding:utf-8 -*-
import json
import matplotlib.pyplot as plt
from DataSrc import Futures, TradeCal, HisQuotes, FutSettle
from flask import Flask, Response

app = Flask(__name__)
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


@app.route("/health")
def health():
    result = {'status': 'UP'}
    return Response(json.dumps(result), mimetype='application/json')


def formatDate(date):
    return date.replace('-', '')


# get future from sqlite3
@app.route("/future")
def getFuture():
    print("request")
    with Futures() as fut:
        res = fut.get_fut()
    # with TradeCal() as tradecal:
    #     res = tradecal.read_sql()
    return Response(json.dumps(res.to_json(orient='records')), mimetype='application/json')


# 8001
@app.route("/8001/<fut>/<futEnd>/<start>/<end>", methods=["GET", "POST"])
def getKData(fut, futEnd, start, end):
    futEnd = formatDate(futEnd)
    start = formatDate(start)
    end = formatDate(end)

    print(futEnd, start, end)
    with HisQuotes() as hq:
        data = hq.getKData(fut=fut, futEnd=futEnd[2:], start=start, end=end)

        print(data)
    return Response(json.dumps(data.to_json(orient='records')), mimetype='application/json')


# 8002: pull data from tushare
@app.route("/8002/<type>/<fut>/<start>/<end>", methods=["GET", "POST"])
def pullData(type, fut=None, start=None, end=None):
    res = {'status': 'sucess', 'type': type}
    rsp = Response(json.dumps(res), mimetype='application/json')

    if type == '1':  # 拉取期货合约信息
        with Futures() as fut:
            fut.pull_data()
        return rsp
    # 暂时：起始时间和结束时间为必须
    start = start.replace('-', '')
    end = end.replace('-', '')
    if type == '2':  # 拉取交易日历（只需要起始日期和结束日期）
        with TradeCal() as tc:
            tc.pull_data(start_date=start, end_date=end)
    elif type == '3':  # 拉取历史行情（拉取某个合约或全部合约的某时间段的历史行情）
        with HisQuotes() as hq:
            hq.pull_data(start_date=start, end_date=end, ts_code=fut)
    elif type == '4':  # 拉取结算参数（拉取某合约或全部合约的某时间段的结算参数）
        with FutSettle() as fs:
            fs.pull_data(start_date=start, end_date=end, ts_code=fut)

    return rsp


# 8003 查询当下合约
@app.route("/800")
def demandFutCode():
    pass
    # 这里不能使用TuShare，需要从交易所官网爬取


from md_demo import Controller

controller = Controller()


# 修改8101支持新增订阅合约：
# 逻辑：python服务启动即链接行情服务，但此时无合约订阅，通过本接口实现添加合约并订阅。理论上是可行的，后续可开发取消某个合约的订阅
@app.route("/8101/<fut>/<futEnd>", methods=["GET", "POST"])
def getQuotes(fut, futEnd):
    # controller.start()
    print("8101订阅")
    futEnd = formatDate(futEnd)
    fut_code = fut + futEnd[2:]
    controller.addFutCode(fut_code=fut_code.lower())
    controller.stop()
    controller.start()

    return "success"


# 8102  取消订阅行情
@app.route("/8102", methods=["GET"])
def stopQuotes():
    print('取消订阅行情')
    controller.stop()
    return "success"


# 8103  更改行情环境
@app.route("/8103/<flag>", methods=["GET", "POST"])
def exchangeEV(flag):
    print('更改行情环境')
    controller.setEV(flag=flag)
    return "success"


if __name__ == "__main__":
    app.run(port=3000, host='0.0.0.0')
