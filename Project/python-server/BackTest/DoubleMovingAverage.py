from BackTest.Strategy import BaseStrategy


class DoubleMovingAverage(BaseStrategy):
    """
    【双均线策略】 created by ZWH 2021-11-04
    """
    def __init__(self):
        super(DoubleMovingAverage, self).__init__()
        # 长线周期默认10天
        self.long_term = 10
        # 短线周期默认5天
        self.short_term = 5
        # 缓存的行情数据(是DataFrame类型)，根据long_term缓存条数
        self.bar_df = None
        self.counts = 0

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
        self.counts += 1
        # （2）bar推送到缓存bar_df
        if self.bar_df is None:
            self.bar_df = bar
        else:
            self.bar_df = self.bar_df.append(bar)
        # （3）判断bar_df的数据是否足够11条，如果不足够，则不做处理；如果足够，进入（4）
        if len(self.bar_df) < 11:
            return
        # （4）取bar_df的最后long_term个元素：bar_df = bat_list.ix[-self.long_term:]
        # 这里不应该截取，截取了后后面的值都不对
        # self.bar_df = self.bar_df.iloc[1:self.long_term + 1]
        # （4）计算barlist的5日均线和10日均线
        short_avg = round(self.bar_df.close.rolling(self.short_term, min_periods=1).mean(), 2)
        long_avg = round(self.bar_df.close.rolling(self.long_term, min_periods=1).mean(), 2)
        ######################### 以上已测试没问题
        # （5）查询持仓
        pos_long, pos_short = self.broker.select_posList()
        # （6）双均线逻辑
        # 价格,以当天的均价成交
        order_price = self.bar_df.close.iloc[-1]
        '''
        2022-02-17 
        这里寻求短期收益，即成交持仓后如果下一次的价格合适立刻平仓
        所以，不可能存在本身有多仓持仓，还多仓成交
        '''
        # 当前bar的价格，再获取最后一次成交单(且是open开仓，平仓跳过此步)的价格看是否合适。这里如果合适，直接平掉仓位；如果不合适，考虑是否要亏损成交
        last_trade = self.broker.get_latest_trade()
        if last_trade is not None:
            if last_trade.operation == 'OPEN':
                if last_trade.direction == 'LONG':
                    self.closeLong(order_price, pos_long)
                else:
                    self.closeShort(order_price, pos_short)
        # 再查询持仓
        pos_long, pos_short = self.broker.select_posList()
        # 短均线上穿长均线，做多（即当前时间点短均线处于长均线上方，前一时间点短均线处于长均线下方）
        if short_avg.iloc[-2] < long_avg.iloc[-2] and short_avg.iloc[-1] >= long_avg.iloc[-1]:
            # 无空仓情况下，直接开多
            if not pos_short:
                print("无空仓，直接开多仓")
                self.openLong(price=order_price, volume=1)
            # 有空仓的情况下，先平空，再开多(开多命令放在on_order_status里面)
            else:
                print("有空仓，先平空仓")   # 平仓手数等于持仓数量
                # 以市价平空仓
                self.closeShort(price=order_price, volume=pos_short)
        # 短均线下穿长均线，做空(即当前时间点短均线处于长均线下方，前一时间点短均线处于长均线上方)
        if long_avg.iloc[-2] < short_avg.iloc[-2] and long_avg.iloc[-1] >= short_avg.iloc[-1]:
            # 无多仓持仓情况下，直接开空
            if not pos_long:
                print("无多仓，直接开空")
                self.openShort(price=order_price, volume=1)
            # 有多仓情况下，先平多，再开空(开空命令放在on_order_status里面)
            else:
                print("有多仓，平多仓")
                # 以市价平多仓
                self.closeLong(price=order_price, volume=pos_long)
