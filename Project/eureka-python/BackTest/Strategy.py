import pandas as pd
# 定义几个常量
SELL = 's'
BUY = 'b'
OPEN = 'o'
CLOSE = 'c'


"""
策略基类：策略类是站在用户的角度，收到行情后什么时候去下单
"""


class BaseStrategy(object):
    broker = None

    def __init__(self):
        super(BaseStrategy, self).__init__()

    def on_start(self):
        """
        策略开始运行
        :return:
        """
        self.broker.sendInfo("策略开始运行")

    def on_stop(self):
        """
        策略运行结束
        :return:
        """
        self.broker.sendInfo("策略运行结束")

    def on_bar(self, bar):
        raise NotImplementedError("请在子类中实现该方法")

    def buy(self, price, volume):
        """
        做多
        :param price: 价格
        :param volume: 数量
        :return:
        """
        self.broker.buy(price, volume)

    def sell(self, price, volume):
        """
        平多
        :param price: 价格
        :param volume: 数量
        :return:
        """
        self.broker.sell(price, volume)

    def short(self, price, volume):
        """
        做空
        :param price: 价格
        :param volume: 数量
        :return:
        """
        self.broker.short(price, volume)

    def cover(self, price, volume):
        """
        平空
        :param price: 价格
        :param volume: 数量
        :return:
        """
        self.broker.cover(price, volume)


"""
【双均线策略】 created by ZWH 2021-11-04
"""


class DoubleMovingAverage(BaseStrategy):
    def __init__(self):
        super(DoubleMovingAverage, self).__init__()
        # 长线周期默认10天
        self.long_term = 10
        # 短线周期默认5天
        self.short_term = 5
        # 缓存的行情数据(是DataFrame类型)，根据long_term缓存条数
        self.bar_df = None
        self.num = 0

    def set_long(self, long):
        """
        设置长线周期
        :param long:
        :return:
        """
        self.long_term = int(long)

    def set_short(self, short):
        """
        设置短线周期
        :param short:
        :return:
        """
        self.short_term = int(short)

    # 实现父类方法，这里是核心，整个策略都在这里。相当于用户报单的逻辑，就是实现什么时候报单、报哪种单(开、平)
    def on_bar(self, bar):
        """
        【策略逻辑】：(1) 当短期均线由下向上穿越长期均线时做多；(2) 当短期均线由上向下穿越长期均线时做空。
        【解释】：（1）短期均线上穿长期均线时：如果没有持空仓，则报（开多仓）单；如果有持空仓，则平空仓。
                （2）短期均线下穿长期均线时：如果没有持多仓，则报（开空仓）单；如果有持多仓，则平多仓。
        【双均线，当缓存到long_term的行情数据时，计算5日均线和10日均线，再往后收到行情判断策略逻辑即可】
        :param bar:
        :return:
        """
        # （1）获取bar
        self.num += 1
        print("双均线收到行情:{}次".format(self.num))
        # （2）bar推送到缓存bar_df
        if self.bar_df is None:
            print(bar)
            self.bar_df = bar
        else:
            print("******")
            self.bar_df.append(bar)
        print(self.bar_df)
        # （3）判断bar_df的数据是否足够11条，如果不足够，则不做处理；如果足够，进入（4）
        if len(self.bar_df) < 11:
            print("return {} 次".format(self.num))
            return
        # （4）取bar_df的最后long_term个元素：bar_df = bat_list.ix[-self.long_term:]
        print(self)
        self.bar_df = self.bar_df[-self.long_term:]
        print("打印bar_df:{}".format(self.bar_df))
        # （4）计算barlist的5日均线和10日均线
        short_avg = round(self.bar_df.close.rolling(self.short_term, min_periods=1).mean(), 2)
        long_avg = round(self.bar_df.close.rolling(self.short_term, min_periods=1).mean(), 2)
        print(short_avg)
        print(long_avg)
        # （5）查询持仓
        pos_long, pos_short = self.broker.select_posList()
        # （6）双均线逻辑
        order_price = self.bar_df[-2].close
        # 短均线下穿长均线，做空(即当前时间点短均线处于长均线下方，前一时间点短均线处于长均线上方)
        if long_avg[-2] < short_avg[-2] and long_avg[-1] >= short_avg[-1]:
            # 无多仓持仓情况下，直接开空
            if not pos_long:
                self.short(price=order_price, volume=1)
            # 有多仓情况下，先平多，再开空(开空命令放在on_order_status里面)
            else:
                # 以市价平多仓
                self.sell(price=order_price, volume=1)
        # 短均线上穿长均线，做多（即当前时间点短均线处于长均线上方，前一时间点短均线处于长均线下方）
        if short_avg[-2] < long_avg[-2] and short_avg[-1] >= long_avg[-1]:
            # 无空仓情况下，直接开多
            if not pos_short:
                self.buy(price=order_price, volume=1)
            # 有空仓的情况下，先平空，再开多(开多命令放在on_order_status里面)
            else:
                # 以市价平空仓
                self.cover(price=order_price, volume=1)