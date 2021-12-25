from Strategy import BaseStrategy
import pandas as pd
import statsmodels.api as sm
import itertools
from statsmodels.tsa.arima.model import ARIMA


class ARIMAStrategy(BaseStrategy):
    """
    【ARIMA策略】 created by ZWH 2021-12-25
    """

    def __init__(self):
        super(ARIMAStrategy, self).__init__()
        # 训练个数
        self.train_nums = 0
        # 训练计数
        self.counts = 0
        # 存放训练个数的行情数据
        self.bar_df = None

    def set_train_nums(self, train_nums):
        """
        设置训练数据个数
        :param train_nums:
        :return:
        """
        self.train_nums = train_nums

    # 实现父类方法，这里是核心，整个策略都在这里。相当于用户报单的逻辑，就是实现什么时候报单、报哪种单(开、平)
    def on_bar(self, bar):
        """
        【策略逻辑】：ARIMA模型实现期货回测
        :param bar:
        :return:
        """
        # 应该从最开始存储train_nums条数据
        if self.bar_df is None:
            self.bar_df = bar
        else:
            self.bar_df = self.bar_df.append(bar)
        self.counts += 1
        # 训练数据到达指定数目，才开始回测
        if self.counts < self.train_nums:
            return
        self.bar_df = self.bar_df[-self.train_nums:]

        df = self.bar_df[['trade_date'], ['close']]
        df.trade_date = pd.to_datetime(df.trade_date)
        df = df.set_index('trade_date')

        p = d = q = range(0, 3)
        pdq = list(itertools.product(p, d, q))

        aic = []
        parameters = []
        for param in pdq:
            try:
                mod = sm.tsa.statespace.SARIMAX(df, order=param, enforce_stationarity=True, enforce_invertibility=True)
                results = mod.fit()
                aic.append(results.aic)
                parameters.append(param)
            except:
                continue
        index_min = min(range(len(aic)), key=aic.__getitem__)
        print(' {} times the optimal model is: ARIMA {} - AIC {}'.format(self.counts - self.train_nums,
                                                                         parameters[index_min],
                                                                         aic[index_min]))
        # 3. 构建并训练模型(df整个的数据拿来训练)
        model = ARIMA(df, order=parameters[index_min])
        model_fit = model.fit()
        # 4. 用这个模型预测bar行情的第二天的价格
        pre_price = model_fit.forecast()
        print('第{}次预测价格为: {}'.format(self.counts-self.train_nums, pre_price))

        # 查询当前持仓
        pos_long, pos_short = self.broker.select_posList()

        # 5. 预测的价格pre_price的当前行情bar的价格做比对 (业务逻辑)
        if bar.close > pre_price:  # 如果预测第二天要涨
            # 判断有无持空仓
            if not pos_short:  # 没有空仓的话，就可以现在买了
                print('无空仓，可开多')
                # 这里有个问题是，应该报几手，暂时报一手单子
                self.buy(price=bar.close, volume=1)
            else:  # 有空仓的话，需要将现在的空仓平掉，防止明天涨价后平仓的话亏本儿
                print('有空仓，平空仓')
                # 统计当前空仓仓位
                self.cover(price=bar.close, volume=pos_short)   # 这里应该要更改，是拿现在所有的仓位手数平

        if bar.close < pre_price:  # 如果预测第二天要跌
            # 判断有无持多仓
            if not pos_long:
                print('无多仓，可开空')
                self.short(price=bar.close, volume=1)
            else:
                print('有多仓，平多仓')
                self.sell(price=bar.close, volume=pos_long)
