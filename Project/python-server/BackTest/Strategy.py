# 定义几个常量
SELL = 's'
BUY = 'b'
OPEN = 'o'
CLOSE = 'c'


class BaseStrategy(object):
    """
    策略基类：策略类是站在用户的角度，收到行情后什么时候去下单
    """
    broker = None

    def __init__(self):
        super(BaseStrategy, self).__init__()

    def on_start(self):
        """
        策略开始运行
        :return:
        """
        self.broker.send_info("策略开始运行")

    def on_stop(self):
        """
        策略运行结束
        :return:
        """
        self.broker.send_info("策略运行结束")

    def on_bar(self, bar):
        raise NotImplementedError("请在子类中实现该方法")

    # def buy(self, price, volume):
    #     """
    #     做多
    #     :param price: 价格
    #     :param volume: 数量
    #     :return:
    #     """
    #     self.broker.buy(price, volume)
    #
    # def sell(self, price, volume):
    #     """
    #     平多
    #     :param price: 价格
    #     :param volume: 数量
    #     :return:
    #     """
    #     self.broker.sell(price, volume)
    #
    # def short(self, price, volume):
    #     """
    #     做空
    #     :param price: 价格
    #     :param volume: 数量
    #     :return:
    #     """
    #     self.broker.short(price, volume)
    #
    # def cover(self, price, volume):
    #     """
    #     平空
    #     :param price: 价格
    #     :param volume: 数量
    #     :return:
    #     """
    #     self.broker.cover(price, volume)

    def openLong(self, price, volume):
        """
        做多
        :param price: 价格
        :param volume: 数量
        :return:
        """
        self.broker.openLong(price, volume)

    def closeLong(self, price, volume):
        """
        平多
        :param price: 价格
        :param volume: 数量
        :return:
        """
        self.broker.closeLong(price, volume)

    def openShort(self, price, volume):
        """
        做空
        :param price: 价格
        :param volume: 数量
        :return:
        """
        self.broker.openShort(price, volume)

    def closeShort(self, price, volume):
        """
        平空
        :param price: 价格
        :param volume: 数量
        :return:
        """
        self.broker.closeShort(price, volume)