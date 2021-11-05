import json
import itertools
import time

import pandas as pd
import requests
import collections
from datetime import datetime
from BackTest.Strategy import BaseStrategy
from DataSrc import HisQuotes

OPEN = 'OPEN'
CLOSE = "CLOSE"
LONG = 'LONG'
SHORT = 'SHORT'


def iterize(iterable):
    niterable = list()
    for elem in iterable:
        if isinstance(elem, str):
            elem = (elem,)
        elif not isinstance(elem, collections.Iterable):
            elem = (elem,)

        niterable.append(elem)

    return niterable


class Order(object):
    def __init__(self, price, volume, direction, operation):
        super(Order, self).__init__()
        self.price = price
        self.volume = volume
        self.direction = direction
        self.operation = operation


"""
这个类的目的是：模拟交易所，推送行情给用户（策略），并实现撮合成交
"""


class BackTester(object):
    def __init__(self):
        super(BackTester, self).__init__()
        # 回测策略类
        self.strategy_class = None
        # 期货合约
        self.ts_code = None
        # 起始日期
        self.start_date = None
        # 结束日期
        self.end_date = None
        # 初始本金.
        self.cash = 1_000_000
        # 策略实例
        self.strategy_instance = None
        # 手续费
        self.commission = 2 / 1000
        # 杠杆比例，默认使用杠杆
        self.leverage = 1.0
        # 滑点率，设置为万5
        self.slipper_rate = 5 / 10000
        # 购买的资产的估值，作为计算爆仓的时候使用.
        self.asset_value = 0
        # 最低保证金比例, 使用bitfinex 的为例子.
        self.min_margin_rate = 0.15
        # 成交单
        self.trades = []
        # 报单列表  数据格式是dataframe格式
        self.active_orders = []
        # 持多仓列表  数据格式是dataframe格式
        self.pos_long = []
        # 持空仓列表  数据格式是dataframe格式
        self.pos_short = []
        # 回测的数据 dataframe数据
        self.backtest_data = None
        # 是否是运行策略优化的方法。
        self.is_optimizing_strategy = False

    def start(self):
        """
        开始回测：外围回测调用本方法
        :return:
        """
        # 先加载数据
        self.init_data()
        # 回放数据
        self.handle_data()
        # 启动策略
        self.run()
        # 回测完成
        self.finish()

    def init_data(self):
        """
        从数据库初始化数据
        :return:
        """
        self.sendInfo("开始加载历史数据")
        time.sleep(1)
        with HisQuotes() as hq:
            self.backtest_data = hq.getData(ts_code=self.ts_code, start=self.start_date, end=self.end_date)
        self.sendInfo("历史数据加载完成")

    # 历史数据回放
    def handle_data(self):
        self.sendInfo("开始回放历史数据")
        # 这里对数据按照日期进行排序
        self.backtest_data = self.backtest_data.sort_values(by="trade_date", ascending=True)
        time.sleep(1)
        self.sendInfo("历史数据回放结束")

    def finish(self):
        """
        回测结束调用，发送回测指标【资金收益率、最大回撤】等
        :return:
        """
        time.sleep(2)
        self.sendInfo("回测完成")

    def set_strategy(self, strategy_class: BaseStrategy):
        """
        设置要跑的策略类.
        :param strategy_class:
        :return:
        """
        self.strategy_class = strategy_class

    def set_tsCode(self, ts_code):
        """
        设置期货合约
        :param ts_code: 期货合约
        :return:
        """
        self.ts_code = ts_code

    def set_data(self, start_date, end_date):
        """
        设置合约起始结束日期
        :param start_date: 开始日期
        :param end_date: 结束日期
        :return:
        """
        self.start_date = start_date
        self.end_date = end_date

    def set_cash(self, cash):
        """
        设置本金
        :param cash: 本金
        :return:
        """
        self.cash = cash

    def set_leverage(self, leverage: float):
        """
        设置杠杆率.
        :param leverage:
        :return:
        """
        self.leverage = leverage

    def set_commission(self, commission: float):
        """
        设置手续费.
        :param commission:
        :return:
        """
        self.commission = commission

    def buy(self, price, volume):
        print(f"开多仓下单: {volume}@{price}")
        order = Order(price, volume, OPEN, LONG)
        self.active_orders.append(order)

    def sell(self, price, volume):
        print(f"平多仓下单: {volume}@{price}")  #
        order = Order(price, volume, CLOSE, LONG)
        self.active_orders.append(order)

    def short(self, price, volume):
        print(f"开空仓下单: {volume}@{price}")
        order = Order(price, volume, OPEN, SHORT)
        self.active_orders.append(order)

    def cover(self, price, volume):
        print(f"平空仓下单: {volume}@{price}")
        order = Order(price, volume, CLOSE, SHORT)
        self.active_orders.append(order)

    def select_posList(self):
        return self.pos_long, self.pos_short

    def set_strategy_instance(self, strategy_instance):
        """
        设置策略实例
        :return:
        """
        self.strategy_instance = strategy_instance

    def run(self):
        # self.strategy_instance = self.strategy_class(self.backtest_data)
        self.strategy_instance.broker = self
        self.strategy_instance.on_start()

        for index, candle in self.backtest_data.iterrows():
            # print(type(bar))
            can = [[candle['trade_date'], candle['open'], candle['close'], candle['high'], candle['low'], candle['vol']]]
            bar = pd.DataFrame(can, columns=['trade_date', 'open', 'close', 'high', 'low', 'volume'])
            self.check_order(bar)                   # 检查该行情bar是否满足成交条件
            self.strategy_instance.on_bar(bar)      # 给到策略（用户）

        self.strategy_instance.on_stop()
        # 统计成交的信息..,可以先在暂时不考虑
        # self.calculate()

    def check_order(self, bar):
        """
        模拟交易所的撮合成交（根据当前这笔行情bar，判断用户已报的单子是否满足成交条件。如果满足，则成交；不满足，跳出）
        :param bar:
        :return:
        """
        # 当前这比行情的价格
        print("查看当前的已报单情况{}".format(self.active_orders))
        for order in self.active_orders:
            price = bar.close
            if order.operation == OPEN:
                print("开仓报单能成交吗？")
                if order.direction == LONG and price <= order.price:   # 开多仓
                    print("开多仓报单成交")
                    # （1）报单记录去掉该单子（2）持仓记录添加该单子 （3）trades成交单+1（4）处理cash，cash-=成交价格*成交量
                    self.cash -= order.price * order.volume
                    self.pos_long.append(order)
                if order.direction == SHORT and price >= order.price:   # 开空仓单子成交
                    print("开空仓报单成交")
                    self.cash += order.price * order.volume
                    self.pos_short.append(order)
                    # 报单记录都是需要pop掉
                    self.active_orders.remove(order)
                    # 成交单都是要push进来
                    self.trades.append(order)
            else:
                if order.direction == LONG and price >= order.prcie:   # 平多仓
                    print("平多仓报单成交")
                    self.cash += order.price * order.volume
                    self.pos_long.remove(order)
                if order.direction == SHORT and price <= order.price:
                    print("平空仓报单成交")
                    self.cash -= order.price * order.volume
                    self.pos_short.remove(order)

        print("查看当前的已报单情况:{}".format(self.active_orders))
        print("查看当前现金:{}".format(self.cash))

    def calculate(self):
        """
        # 拿到成交的信息，把成交的记录统计出来.夏普率、 盈亏比、胜率、 最大回撤 年化率/最大回撤
        :return:
        """
        for trade in self.trades:
            """
             order_id 
             trade_id
             price,
             volume 
             
             10000 --> 1BTC
             12000 --> 1BTC  -- >  2000
            """
            pass

    def optimize_strategy(self, **kwargs):
        """
        优化策略， 参数遍历进行..，如双均线策略，遍历长短周期值
        :param kwargs:
        :return:
        """
        self.is_optimizing_strategy = True

        optkeys = list(kwargs)
        vals = iterize(kwargs.values())
        optvals = itertools.product(*vals)
        optkwargs = map(zip, itertools.repeat(optkeys), optvals)
        optkwargs = map(dict, optkwargs)  # dict value...

        for params in optkwargs:
            print(params)

        # 参数列表, 要优化的参数, 放在这里.
        cash = self.cash
        leverage = self.leverage
        commission = self.commission
        for params in optkwargs:
            self.strategy_class.params = params
            self.set_cash(cash)
            self.set_leverage(leverage)
            self.set_commission(commission)
            self.run()

    # 获取当前系统时间
    def getNowTime(self):
        return datetime.strftime(datetime.now(), "%H:%M:%S")

    def sendInfo(self, info):
        re = {'info': '[' + self.getNowTime() + ']' + info}
        url = "http://localhost:5678/sendDoubleMABackTestInfo"
        headers = {'Content-type': 'application/json'}
        requests.post(url, data=json.dumps(re), headers=headers)

