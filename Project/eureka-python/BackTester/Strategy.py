import sqlite3 as sql3


# 暂时只实现（历史回测）
# 策略基类:策略里不要获取数据，放到回测管理类里
class Strategy(object):
    def __init__(self):
        self.conn = sql3.connect('DBName')


class DoubleMovingAverage(Strategy):
    def __init__(self, long, short):
        super(DoubleMovingAverage, self).__init__()
        self.long = long
        self.short = short


