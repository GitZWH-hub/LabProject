import json
import itertools
import random
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


# 报单信息
class Order(object):
    def __init__(self, order_no, price, volume, operation, direction):
        super(Order, self).__init__()
        self.order_no = order_no
        self.price = price
        self.volume = volume
        self.operation = operation
        self.direction = direction

    def __str__(self):
        return f"{self.order_no} {self.price} {self.volume} {self.direction} {self.operation}"


# 成交单信息
class Match(object):
    def __init__(self, order_no, match_no, price, volume, operation, direction):
        super(Match, self).__init__()
        self.order_no = order_no
        self.match_no = match_no
        self.price = price
        self.volume = volume
        self.operation = operation
        self.direction = direction

    def __str__(self):
        return f"{self.order_no} {self.match_no} {self.price} {self.volume} {self.direction} {self.operation}"


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
        self.cash = 10000000
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
        # 持多仓数量
        self.pos_long = 0
        # 持空仓数量
        self.pos_short = 0
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
        self.cash = int(cash)

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
        order = Order(self.generate_orderNo(), price, volume, OPEN, LONG)
        self.active_orders.append(order)

    def sell(self, price, volume):
        print(f"平多仓下单: {volume}@{price}")  #
        order = Order(self.generate_orderNo(), price, volume, CLOSE, LONG)
        self.active_orders.append(order)

    def short(self, price, volume):
        print(f"开空仓下单: {volume}@{price}")
        order = Order(self.generate_orderNo(), price, volume, OPEN, SHORT)
        self.active_orders.append(order)

    def cover(self, price, volume):
        print(f"平空仓下单: {volume}@{price}")
        order = Order(self.generate_orderNo(), price, volume, CLOSE, SHORT)
        self.active_orders.append(order)

    def select_posList(self):
        return self.pos_long, self.pos_short

    def generate_orderNo(self):
        """
        生成报单号: 由'O'+ 豪秒级时间戳13位 + 2位随机数
        :return: 返回报单号
        """
        now = str(int(round(time.time() * 1000)))
        order_no = "O" + now + str(random.randint(10, 99))
        return order_no

    def generate_matchNo(self):
        """
        生成成交单号：由'M' + 豪秒级时间戳13位 + 三位随机数
        :return: 返回成交单号
        """
        now = str(int(round(time.time() * 1000)))
        match_no = "M" + now + str(random.randint(10, 99))
        return match_no

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
            can = [[candle['trade_date'], float(candle['open']), float(candle['close']),
                    float(candle['high']), float(candle['low']), float(candle['vol'])]]
            bar = pd.DataFrame(can, columns=['trade_date', 'open', 'close', 'high', 'low', 'volume'])
            self.check_order(bar)                   # 检查该行情bar是否满足成交条件
            self.strategy_instance.on_bar(bar)      # 给到策略（用户）
            self.strategy_instance.on_bar(bar)      # 给到策略（用户）

        self.strategy_instance.on_stop()
        self.print_allInfo()
        # 统计成交的信息..,可以先在暂时不考虑
        # self.calculate()

    def print_allInfo(self):
        """
        打印查看信息
        :return:
        """
        print("当前报单：")
        for i in self.active_orders:
            print(i)
        print("当前成交单：")
        for i in self.trades:
            print(i)
        print("当前多仓仓位: {}".format(self.pos_long))
        print("当前空仓仓位: {}".format(self.pos_short))

    def check_order(self, bar):
        """
        模拟交易所的撮合成交（根据当前这笔行情bar，判断用户已报的单子是否满足成交条件。如果满足，则成交；不满足，跳出）
        :param bar:
        :return:
        """
        # 当前这比行情的价格
        print("查看当前的已报单情况{}".format(self.active_orders))
        for order in self.active_orders:
            price = bar.close.iloc[0]
            # 成交单
            match = None
            print('报单价格：{}'.format(order.price), '行情价格：{}'.format(price))
            print(order.direction, order.operation)
            if order.operation == OPEN:
                if order.direction == LONG and price <= order.price:   # 开多仓
                    print("开多仓报单成交")
                    # （1）报单记录去掉该单子（2）持仓记录添加该单子 （3）trades成交单+1（4）处理cash，cash-=成交价格*成交量
                    self.cash -= order.price * order.volume
                    # 生成成交单
                    match = Match(order.order_no, self.generate_matchNo(), order.price, order.volume, order.operation, order.direction)
                    # 仓位append
                    self.pos_long += order.volume
                if order.direction == SHORT and price >= order.price:   # 开空仓
                    print("开空仓报单成交")
                    self.cash += order.price * order.volume
                    # 生成成交单
                    match = Match(order.order_no, self.generate_matchNo(), order.price, order.volume, order.operation, order.direction)
                    # 仓位append
                    self.pos_short += order.volume
            else:
                if order.direction == LONG and price >= order.price:   # 平多仓
                    print("平多仓报单成交")
                    self.cash += order.price * order.volume
                    # 生成成交单
                    match = Match(order.order_no, self.generate_matchNo(), order.price, order.volume, order.operation, order.direction)
                    # 平多仓成交，需要将多仓remove掉该仓位, 根据报单号删除这个成交仓位
                    self.pos_long -= order.volume
                if order.direction == SHORT and price <= order.price:
                    print("平空仓报单成交")
                    self.cash -= order.price * order.volume
                    # 生成成交单
                    match = Match(order.order_no, self.generate_matchNo(), order.price, order.volume, order.operation, order.direction)
                    self.pos_short -= order.volume
            # 如果成交了，报单记录都是需要remove掉
            if match is not None:
                self.active_orders.remove(order)
                # 成交单都是要push进来
                self.trades.append(match)
        print("查看当前的已报单情况:{}".format(self.active_orders))
        print("查看当前现金:{}".format(self.cash))

    def calculate(self):
        """
        # 拿到成交的信息，把成交的记录统计出来.夏普率、 盈亏比、胜率、 最大回撤 年化率/最大回撤
        :return:
        """
        for trade in self.trades:

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

    # 获取当前系统时间(时：分：秒)
    def getNowTime(self):
        return datetime.strftime(datetime.now(), "%H:%M:%S")

    def sendInfo(self, info):
        re = {'info': '[' + self.getNowTime() + ']' + info}
        url = "http://localhost:5678/sendDoubleMABackTestInfo"
        headers = {'Content-type': 'application/json'}
        requests.post(url, data=json.dumps(re), headers=headers)

