from Strategy import BaseStrategy
import pandas as pd
import matplotlib.pyplot as plt
import statsmodels.api as sm
import itertools
from statsmodels.tsa.arima.model import ARIMA
import warnings
from sklearn import metrics


class ARIMAStrategy(BaseStrategy):
    """
    【ARIMA策略】 created by ZWH 2021-12-25
    """
    def __init__(self):
        super(ARIMAStrategy, self).__init__()
        # 训练个数
        self.train_nums = 0
        # 存放训练个数的历史结算价格
        self.train_orices = []

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
        # 1. 获取数据 —— CSV文件
        data = pd.read_csv('./Data/AAPL.csv')
        data = data.iloc[::-1]
        print(data.head())
        # 只保留时间和结算价
        df = data[['Date', 'Close']]
        df.Date = pd.to_datetime(df.Date)
        df = df.set_index('Date')

        # 2. 求ARIMA最合适的阶数
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
        print('the optimal model is: ARIMA {} - AIC {}'.format(parameters[index_min], aic[index_min]))

        # 训练集：取df总长度的 10分之9
        TRAIN = int(len(df) * 9 / 10)
        # 测试集：forecast剩余的 10分之2
        TEST = len(df) - TRAIN

        # 3. 构建并训练模型
        model = ARIMA(df[:TRAIN], order=parameters[index_min])
        model_fit = model.fit()

        # 4. 模型预测
        # 求df在前TRAIN数据的起始截止日期
        pre_begin = (df.index[0]).strftime("%Y-%m-%d %H:%M:%S")[:7]
        pre_end =  (df.index[TRAIN-1]).strftime("%Y-%m-%d %H:%M:%S")[:10]
        # predict和forecast的区别：predict只能是训练集内部的数据，forecast可以预测外部数据
        # 这里直接predict200条已训练数据，并forecast了df剩下的数据
        pred = model_fit.predict(start=pre_begin, end=pre_end, typ='levels')
        pred2 = model_fit.forecast(TEST)

        index_key = df.index[TRAIN:]
        test = pd.Series(pred2.tolist(), index=index_key)
        # pred = pred.append(pd.Series(test))
        pred3 = pd.Series(test)

        # 5. 模型评估
        # 测试集真实值
        y_true = df.Close[TRAIN:]
        # 测试集预测值
        y_pred = pred2.tolist()