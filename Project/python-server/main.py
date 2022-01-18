#!/usr/bin/env python
# -*-coding:utf-8 -*-
import json
import matplotlib.pyplot as plt
from DataSrc import Futures, TradeCal, HisQuotes, FutSettle
from flask import Flask, Response
from BackTest.BackTest import BackTester
from BackTest.DoubleMovingAverage import DoubleMovingAverage
from BackTest.ARIMA import ARIMAStrategy

# 数据挖掘，待删除
from Model import Model

app = Flask(__name__)
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']  # 用来正常显示中文标签
plt.rcParams['axes.unicode_minus'] = False  # 用来正常显示负号


@app.route("/health")
def health():
    result = {'status': 'UP'}
    return Response(json.dumps(result), mimetype='application/json')


def formatDate(date):
    return date.replace('-', '')


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
@app.route("/8002/<type>/<exchange>/<start>/<end>", methods=["GET", "POST"])
def pullData(type, exchange, start, end):
    res = {'status': 'sucess', 'type': type}
    rsp = Response(json.dumps(res), mimetype='application/json')

    # 期货合约信息
    if type == '1':
        with Futures() as fut:
            fut.setExchange(exchange=exchange)
            fut.pull_data()
        return rsp

    start = start.replace('-', '')
    end = end.replace('-', '')
    # 交易日历
    if type == '2':
        with TradeCal() as tc:
            tc.setExchange(exchange=exchange)
            tc.pull_data(start_date=start, end_date=end)
    # 历史行情
    elif type == '3':
        with HisQuotes() as hq:
            hq.setExchange(exchange=exchange)
            hq.pullData(start_date=start, end_date=end)
    # 结算参数
    elif type == '4':
        with FutSettle() as fs:
            fs.setExchange(exchange=exchange)
            fs.pull_data(start_date=start, end_date=end)

    return rsp


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


# 8105  双均线回测
@app.route("/8105/<fut>/<start>/<end>/<short>/<long>/<cash>", methods=["GET", "POST"])
def doubleMABackTest(fut, start, end, short, long, cash):
    print("开始双均线回测")
    start = start.replace('-', '')
    end = end.replace('-', '')
    """
    设置策略实例参数
    """
    # 双均线策略
    doubleMABT = DoubleMovingAverage()
    # 设置长线周期
    doubleMABT.set_long(long)
    # 设置短线周期
    doubleMABT.set_short(short)
    """
    设置回测模块相关的参数
    """
    # 回测
    backTester = BackTester()
    # 设置策略类
    backTester.set_strategy_instance(doubleMABT)
    # 设置初始资金
    backTester.set_cash(cash)
    # 设置期货代码
    backTester.set_tsCode(fut)
    # 设置起始结束日期
    backTester.set_date(start, end)
    # 启动回测
    backTester.start()

    return 'success'


# 8106  ARIMA策略回测
@app.route("/8106/<fut>/<start>/<end>/<cash>/<nums>", methods=["GET", "POST"])
def ARIMAtest(fut, start, end, cash, nums):
    print("开始ARIMA策略回测")
    start = start.replace('-', '')
    end = end.replace('-', '')
    """
    设置策略实例参数
    """
    ARIMA_instance = ARIMAStrategy()
    ARIMA_instance.set_train_nums(int(nums))
    """
    设置回测模块相关的参数
    """
    # 回测
    backTester = BackTester()
    # 设置策略类
    backTester.set_strategy_instance(ARIMA_instance)
    # 设置初始资金
    backTester.set_cash(cash)
    # 设置期货代码
    backTester.set_tsCode(fut)
    # 设置起始结束日期
    backTester.set_date(start, end)
    # 启动回测
    backTester.start()

    return 'success'


if __name__ == "__main__":
    app.run(port=3001, host='0.0.0.0')
