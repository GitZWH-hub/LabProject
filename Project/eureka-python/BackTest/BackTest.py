"""
created by ZWH 2021-11-01
回测模块
"""

import json, time, random
import itertools, collections
import pandas as pd
import requests
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


def get_now():
    """
    获取当前系统时间
    :return: 返回字符串 "时：分：秒"
    """
    return datetime.strftime(datetime.now(), "%H:%M:%S")


class Order(object):
    """
    报单
    """
    def __init__(self, order_no, price, volume, operation, direction):
        super(Order, self).__init__()
        self.order_no = order_no
        self.price = price
        self.volume = volume
        self.operation = operation
        self.direction = direction

    def __str__(self):
        return f"{self.order_no} {self.price} {self.volume} {self.direction} {self.operation}"


class Match(object):
    """
    成交单
    """
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


class BackTester(object):
    """
    这个类的目的是：模拟交易所的功能【推送行情给用户（策略）】、【撮合成交】、【记录报单、成交信息】、【计算策略评价指标】、【策略优化】
    """
    def __init__(self):
        super(BackTester, self).__init__()
        # 期货合约
        self.ts_code = None
        # 起始日期
        self.start_date = None
        # 结束日期
        self.end_date = None
        # 初始本金
        self.cash = 10000000
        # 策略实例
        self.strategy_instance = None
        # 手续费
        self.commission = 2 / 1000
        # 杠杆比例，默认使用杠杆
        self.leverage = 1.0
        # 滑点率，设置为万5
        self.slipper_rate = 5 / 10000
        # 购买的资产的估值，作为计算爆仓的时候使用
        self.asset_value = 0
        # 最低保证金比例
        self.min_margin_rate = 0.15
        # 成交单记录
        self.trades = []
        # 报单列表dataframe
        self.active_orders = []
        # 持多仓数量
        self.pos_long = 0
        # 持空仓数量
        self.pos_short = 0
        # 回测的数据 dataframe格式
        self.backtest_data = None
        # 是否运行策略优化的方法
        self.is_optimizing_strategy = False
        # 回测策略类，暂时不需要set
        self.strategy_class = None

    def start(self):
        """
        开始回测：外围回测调用本方法
        :return:
        """
        # 加载数据
        self.init_data()
        # 回放数据
        self.handle_data()
        # 启动策略
        self.run()
        # 回测完成
        self.finish()
        # 策略优化

    def init_data(self):
        """
        从数据库初始化数据
        :return:
        """
        self.send_info("开始加载历史数据")
        time.sleep(1)
        with HisQuotes() as hq:
            self.backtest_data = hq.getData(ts_code=self.ts_code, start=self.start_date, end=self.end_date)
        self.send_info("历史数据加载完成")

    # 历史数据回放
    def handle_data(self):
        self.send_info("开始回放历史数据")
        # 这里对数据按照日期进行排序
        self.backtest_data = self.backtest_data.sort_values(by="trade_date", ascending=True)
        # 还要观察数据有没有坏点（TuShare拉下来的数据有的字段是NULL，需要预处理一下）
        time.sleep(1)
        self.send_info("历史数据回放结束")

    def finish(self):
        """
        回测结束调用，发送回测指标【资金收益率、最大回撤等】
        :return:
        """
        time.sleep(1)
        # 推送策略评价结果
        self.send_strategy_result()
        # 回测完成
        self.send_info("回测完成")

    def set_strategy(self, strategy_class: BaseStrategy):
        """
        设置要跑的策略类
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

    def set_date(self, start_date, end_date):
        """
        设置回测起始日期、结束日期
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

    def set_is_optimizing_strategy(self, ifyes):
        """
        设置是否调优寻找最优参数
        :param ifyes: bool型
        :return:
        """
        self.is_optimizing_strategy = ifyes

    def set_leverage(self, leverage: float):
        """
        设置杠杆率
        :param leverage:
        :return:
        """
        self.leverage = leverage

    def set_commission(self, commission: float):
        """
        设置手续费率
        :param commission:
        :return:
        """
        self.commission = commission

    '''
    不需要计算报单手续费，正常情况下：报单，冻结手续费，如果撤单或成交需要解冻手续费
    这里只需要在成交时计算成交手续费并扣除即可
    '''
    def buy(self, price, volume):
        """
        开多仓报单
        :param price: 报单价格
        :param volume: 报单手数
        :return:
        """
        print(f"开多仓下单: {volume}@{price}")
        order = Order(self.generate_orderNo(), price, volume, OPEN, LONG)
        self.active_orders.append(order)

    def sell(self, price, volume):
        """
        平多仓下单
        平仓报单的价格要看之前开仓成交的成交价：
        如开多仓成交的成交价是70000，则如果要赚钱的话，平仓报单的价格应该要大于70000；所以这里可能要查看成交信息确定自己的报单价格。
        还有报单手数怎么确定？
        :param price: 报单价格
        :param volume: 报单手数
        :return:
        """
        print(f"平多仓下单: {volume}@{price}")  #
        order = Order(self.generate_orderNo(), price, volume, CLOSE, LONG)
        self.active_orders.append(order)

    def short(self, price, volume):
        """
        开空仓下单
        :param price: 报单价格
        :param volume: 报单手数
        :return:
        """
        print(f"开空仓下单: {volume}@{price}")
        order = Order(self.generate_orderNo(), price, volume, OPEN, SHORT)
        self.active_orders.append(order)

    def cover(self, price, volume):
        """
        平空仓下单
        平仓报单的价格要看之前开仓成交的成交价：
        如开多仓成交的成交价是70000，则如果要赚钱的话，平仓报单的价格应该要大于70000；所以这里可能要查看成交信息确定自己的报单价格。
        :param price: 报单价格
        :param volume: 报单手数
        :return:
        """
        print(f"平空仓下单: {volume}@{price}")
        order = Order(self.generate_orderNo(), price, volume, CLOSE, SHORT)
        self.active_orders.append(order)

    def select_posList(self):
        """
        返回多仓和空仓仓位数量
        :return: 多仓仓位量、空仓仓位量
        """
        return self.pos_long, self.pos_short

    def generate_orderNo(self):
        """
        生成报单号。报单号：'O' + 13位豪秒级时间戳 + 2位随机数
        :return: 返回报单号
        """
        now = str(int(round(time.time() * 1000)))
        order_no = "O" + now + str(random.randint(10, 99))
        return order_no

    def generate_matchNo(self):
        """
        生成成交单号。成交单号：'M' + 13位豪秒级时间戳 + 2位随机数
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
        """
        启动
        :return:
        """
        # 策略实例绑定self
        self.strategy_instance.broker = self
        # 启动策略
        self.strategy_instance.on_start()

        for index, candle in self.backtest_data.iterrows():
            can = [[candle['trade_date'], float(candle['open']), float(candle['close']),
                    float(candle['high']), float(candle['low']), float(candle['vol'])]]
            bar = pd.DataFrame(can, columns=['trade_date', 'open', 'close', 'high', 'low', 'volume'])
            self.check_order(bar)                       # 检查该行情bar是否满足成交条件
            self.strategy_instance.on_bar(bar)          # 给到策略（用户）
            # 打印相关信息
            self.print_allInfo()

        # 停止策略
        self.strategy_instance.on_stop()
        # 计算策略指标
        # self.calculate()

    def print_allInfo(self):
        """
        打印查看信息
        :return:
        """
        print("*" * 55)
        print("当前报单：")
        for i in self.active_orders:
            print("      {}".format(i))
        print("当前成交单：")
        for i in self.trades:
            print("      {}".format(i))
        print("当前多仓仓位: {}".format(self.pos_long))
        print("当前空仓仓位: {}".format(self.pos_short))
        print("当前现金cash: {}".format(self.cash))

    def check_order(self, bar):
        """
        模拟交易所的撮合成交（根据当前这笔行情bar，判断用户已报的单子是否满足成交条件。如果满足，则成交；不满足，跳出）
        :param bar:
        :return:
        """
        # 当前这比行情的价格
        for order in self.active_orders:
            price = bar.close.iloc[0]
            # 成交单
            match = None
            """
            【这里撮合成交的价格仍有待考虑和修改，目前就以报单价格成交】
            【实际上的成交价依据前一笔成交价而定出最新成交价】如果前一笔成交价低于或等于卖出价，则最新成交价就是卖出价；
                                                     如果前一笔成交价高于或等于买入价，则最新成交价就是买入价；
                                                     如果前一笔成交价在卖出价与买入价之间，则最新成交价就是前一笔的成交价。
            """
            if order.operation == OPEN:
                if order.direction == LONG and price <= order.price:    # 开多仓
                    print("开多仓报单成交")
                    # （1）报单记录去掉该单子（2）持仓数+volume（3）trades成交单+1（4）处理cash，cash-=成交价格*成交量
                    self.cash -= order.price * order.volume
                    # 生成成交单
                    match = Match(order.order_no, self.generate_matchNo(), order.price, order.volume, order.operation, order.direction)
                    # 仓位数增加
                    self.pos_long += order.volume
                if order.direction == SHORT and price >= order.price:   # 开空仓
                    print("开空仓报单成交")
                    self.cash += order.price * order.volume
                    match = Match(order.order_no, self.generate_matchNo(), order.price, order.volume, order.operation, order.direction)
                    self.pos_short += order.volume
            else:
                if order.direction == LONG and price >= order.price:    # 平多仓
                    print("平多仓报单成交")
                    self.cash += order.price * order.volume
                    match = Match(order.order_no, self.generate_matchNo(), order.price, order.volume, order.operation, order.direction)
                    # 平多仓成交，需要将多仓remove掉该仓位, 根据报单号删除这个成交仓位
                    self.pos_long -= order.volume
                if order.direction == SHORT and price <= order.price:   # 平空仓
                    print("平空仓报单成交")
                    self.cash -= order.price * order.volume
                    match = Match(order.order_no, self.generate_matchNo(), order.price, order.volume, order.operation, order.direction)
                    self.pos_short -= order.volume
            # 如果成交了，报单记录需要remove掉
            if match is not None:
                self.active_orders.remove(order)
                # 成交单都是要push进来
                self.trades.append(match)

    def calculate(self):
        """
        计算策略评价指标。如夏普率、盈亏比、胜率、最大回撤、年化率等
        这边可能需要根据成交单来计算，或者添加其他的记录。
        :return:
        """
        for trade in self.trades:
            pass

    def optimize_strategy(self, **kwargs):
        """
        优化策略。参数遍历进行，如双均线策略，遍历长短周期值
        :param kwargs: 策略个性化参数（字典参数）
        :return:
        """
        if self.is_optimizing_strategy:
            self.send_info("运行策略优化")
            optkeys = list(kwargs)
            vals = iterize(kwargs.values())
            optvals = itertools.product(*vals)
            optkwargs = map(zip, itertools.repeat(optkeys), optvals)
            optkwargs = map(dict, optkwargs)

            for params in optkwargs:
                print(params)

            # 参数列表, 要优化的参数, 放在这里.
            cash = self.cash
            # leverage = self.leverage
            # commission = self.commission
            for params in optkwargs:
                self.strategy_class.params = params
                self.set_cash(cash)
                # self.set_leverage(leverage)
                # self.set_commission(commission)
                self.run()
            # 这边计算出最优的参数

    def send_info(self, info):
        """
        推送消息给客户端
        :param info: 消息内容
        :return:
        """
        res = {'info': '[' + get_now() + '] ' + info}
        url = "http://localhost:5001/sendDoubleMABackTestInfo"
        headers = {'Content-type': 'application/json'}
        requests.post(url, data=json.dumps(res), headers=headers)

    def send_strategy_result(self):
        """
        推送策略指标给客户端
        :return:
        """
