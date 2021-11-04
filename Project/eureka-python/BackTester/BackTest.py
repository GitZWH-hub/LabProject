import time
from datetime import datetime
import requests
import json


# 获取当前系统时间
def getNowTime():
    return datetime.strftime(datetime.now(), "%H:%M:%S")


class BackTester(object):
    def __init__(self, start_date, end_date, ts_code, cash, strategy):
        self.start_date = start_date
        self.end_date = end_date
        self.ts_code = ts_code
        self.cash = cash
        # 策略对象，这里先使用双均线策略测试
        self.strategy = strategy
        self.url = "http://localhost:5678/sendDoubleMABackTestInfo"
        self.headers = {'Content-type': 'application/json'}

    # 开始回测
    def start_backtester(self):
        # 先加载数据
        self.init_data()
        # 回放数据
        self.handle_data()
        # 策略启动
        # self.strategy.start()

    # 初始化历史数据
    def init_data(self):
        self.sendTo("开始加载历史数据")
        time.sleep(2)
        self.sendTo("历史数据加载完成")

    # 历史数据回放
    def handle_data(self):
        self.sendTo("开始回放历史数据")
        time.sleep(5)
        self.sendTo("历史数据回放结束")

    def sendTo(self, info):
        re = {'info': '[' + getNowTime() + ']' + info}
        requests.post(self.url, data=json.dumps(re), headers=self.headers)


