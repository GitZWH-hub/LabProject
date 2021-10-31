#!/usr/bin/env python
# -*-coding:utf-8 -*-
import json
import tushare as ts
import sqlite3 as sql3
from logfile import log, Logger
from datetime import datetime
import pandas as pd

'''
基类
Created on Sept 27, 2021    @Author: zwh
'''


class Base(object):
    def __init__(self):
        Logger()
        self.token = 'f0d2ecb5970c108c5959d1b445fb99e55690038748029204c0df86ec'
        self.pro = ts.pro_api(self.token)
        self.exchange = 'SHFE'
        self.DBNAME = 'DBData'

    def __enter__(self):
        self.conn = sql3.connect(self.DBNAME)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def read_sql(self):
        data = pd.read_sql_query("select *from " + self.TABLENAME, self.conn)
        print(data.head())


'''
获取SHFE的期货合约信息: TuShare
Created on Sept 27, 2021    @Author: zhangwh
'''


class Futures(Base):
    def __enter__(self):
        super(Futures, self).__enter__()  # 【如果要继承父类的函数并重写，需要加一句: super(子类, self).函数名()】
        self.TABLENAME = 'Futures'
        return self

    def pull_data(self):
        log.info('-- 开始拉取合约信息(Future) --')
        data = self.pro.fut_basic(exchange=self.exchange, fut_type='1')
        try:  # index:是否插入索引，默认插入   if_exists:replace、append、fail
            data.to_sql(self.TABLENAME, self.conn, index=True, if_exists='replace')
        except:
            log.error("to_sql ERROR")
        log.info('-- 拉取合约信息结束(Future) --')

    def get_fut(self):
        futs = pd.read_sql_query("select * from " + self.TABLENAME, self.conn)
        return futs.head()

    def get_ts_code(self, fut_code):
        ts_code = pd.read_sql_query("select ts_code from " + self.TABLENAME + " where fut_code = '" + fut_code + "'",
                                    self.conn)
        return ts_code


'''
获取SHFE交易日历: TuShare
Created on Oct 5, 2021  @Author: zhangwh
'''


class TradeCal(Base):
    def __enter__(self):
        super(TradeCal, self).__enter__()
        self.TABLENAME = 'TradeCal'
        return self

    def pull_data(self, start_date, end_date):
        log.info('-- 开始获取交易日历(TradeCal) --')
        try:
            data = self.pro.trade_cal(exchange=self.exchange, start_date=start_date, end_date=end_date)
            data.to_sql(self.TABLENAME, self.conn, index=True, if_exists='replace')
        except:
            log.error('to_sql ERROR')
        log.info('-- 拉取交易日历结束(TradeCal) --')


'''
获取SHFE历史行情信息: TuShare
Created on Oct 5, 2021  @Author: zhangwh
'''


class HisQuotes(Base):
    def __enter__(self):
        super(HisQuotes, self).__enter__()
        self.TABLENAME = 'HisQuotes'
        return self

    def pull_data_(self, start_date=None, end_date=None, ts_code=None):
        # 考虑几种情况
        # 1. 拉取CU的所有历史数据，此时start_date和end_date=None
        #    此时使用 需要先查取Futures  的所有该合约的期货代码ts_code循环利用下面的语句拉数据
        #    self.pro.fut_daily(ts-code=ts_code)

        log.info('-- 开始拉取历史行情(HisQuotes) --')
        try:
            with Futures() as future:
                if ts_code is not None:
                    data = self.pro.fut_daily(ts_code=ts_code + '.SHF', start_date=start_date, end_date=end_date)
                    data.to_sql(ts_code, self.conn, index=True, if_exists='replace')
                    return
                futures = future.get_fut()
                futs = futures['ts_code']
                for fut in futs:
                    log.info('  获取' + fut + '行情')
                    data = self.pro.fut_daily(ts_code=fut, start_date=start_date, end_date=end_date)
                    data.to_sql(fut, self.conn, index=True, if_exists='replace')
                    log.info('  结束')
        except:
            log.error("to_sql ERROR")
        log.info('-- 拉取历史行情结束(HisQuotes) --')

    def pull_data(self, ts_code, start_date=None, end_date=None):
        try:
            with Futures() as fut:
                ts_codes = fut.get_ts_code(fut_code=ts_code)

                for index, row in ts_codes.iterrows():
                    print(row)
                    print(row['ts_code'])
                    data = self.pro.fut_daily(ts_code=row['ts_code'])
                    print(data)
                    data.to_sql(ts_code, self.conn, index=True, if_exists='append')
        except:
            log.error("sql error")

    def getKData(self, fut, futEnd, start, end):
        try:
            print("select trade_date,ts_code,open,close,high,low from " +
                  fut + " where ts_code = '" + fut + futEnd + ".SHF' and trade_date between '" + start + "' and '" + end + "'")
            data = pd.read_sql_query("select trade_date,ts_code,open,close,high,low from " +
                                     fut + " where ts_code = '" + fut + futEnd + ".SHF' and trade_date between '" + start + "' and '" + end + "'",
                                     self.conn)
            print("啊啊啊啊啊，出错了")
            return data
        except:
            log.info("ERROR")


'''
获取SHFE结算参数: TuShare
Created on Oct 5, 2021  @Author: zhangwh
'''


class FutSettle(Base):
    def __enter__(self):
        super(FutSettle, self).__enter__()
        self.TABLENAME = 'FutSettle'
        return self

    def pull_data(self, start_date=None, end_date=None, ts_code=None):
        log.info('-- 开始获取结算参数(FutSettle)')
        try:
            # fut_settle接口中，ts_code和trade_date至少需要一个
            # data = self.pro.fut_settle(trade_date=trade_date, ts_code=ts_code, exchange=self.exchange)
            data = self.pro.fut_settle(ts_code=ts_code, exchange=self.exchange, start_date=start_date,
                                       end_date=end_date)
            data.to_sql(self.TABLENAME, self.conn, index=True, if_exists='replace')
        except:
            log.error('to_sql ERROR')
        log.info('-- 拉取结算参数结束(FutSettle) --')


'''
爬虫SHFE基类
Created on Oct 10, 2021  @Author: zhangwh
'''

'''
获取 Trade Para(爬虫): SHFE
Created on Oct 10, 2021  @Author: zhangwh
'''

from urllib.request import urlopen
import pandas as pd


# load data by trade date. if it is not trade day, there will be an error
class TradePara(object):
    def __init__(self):
        self.now_date = datetime.strftime(datetime.now(), '%Y%m%d')
        self.DBNAME = 'DBData'
        self.TABLENAME = 'TradePara'

    def __enter__(self):
        self.conn = sql3.connect(self.DBNAME)
        self.url = 'http://www.shfe.com.cn/data/instrument/ContractDailyTradeArgument'
        return self

    # only on trade day
    def loadData(self, trade_date=None):
        self.url += trade_date + '.dat' if trade_date else self.now_date + '.dat'
        html = urlopen(self.url).read().decode('utf8').encode('utf8')
        myJson = json.loads(html)
        # open DB to save data
        try:
            # json to dataframe
            real = myJson['ContractDailyTradeArgument']
            for ct in real:
                ct['HDEGE_LONGMARGINRATIO'] = float('0' + ct['HDEGE_LONGMARGINRATIO'])
                ct['HDEGE_SHORTMARGINRATIO'] = float('0' + ct['HDEGE_SHORTMARGINRATIO'])
                ct['LOWER_VALUE'] = float('0' + ct['LOWER_VALUE'])
                ct['SPEC_LONGMARGINRATIO'] = float('0' + ct['SPEC_LONGMARGINRATIO'])
                ct['SPEC_SHORTMARGINRATIO'] = float('0' + ct['SPEC_SHORTMARGINRATIO'])
                ct['UPPER_VALUE'] = float('0' + ct['UPPER_VALUE'])
                ct['INSTRUMENTID'] = (ct['INSTRUMENTID']).upper()
            data = pd.DataFrame(real)
            data.to_sql(self.TABLENAME, self.conn, index=True, if_exists='replace')
        except:
            log.error("sql error")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

# if __name__ == "__main__":
#     with TradePara() as tp:
#         tp.loadData(trade_date='20211008')
#     conn = sql3.connect('DBData')
#     data = [{'fut_code': 'cu', 'para': '铜'}, {'fut_code': 'bc', 'para': '铜BC'}, {'fut_code': 'al', 'para': '铝'}, {'fut_code': 'zn', 'para': '锌'},
#             {'fut_code': 'pb', 'para': '铅'}, {'fut_code': 'ni', 'para': '镍'}, {'fut_code': 'sn', 'para': '锡'}, {'fut_code': 'au', 'para': '黄金'},
#             {'fut_code': 'ag', 'para': '白银'}, {'fut_code': 'rb', 'para': '螺纹钢'}, {'fut_code': 'wr', 'para': '线材'}, {'fut_code': 'hc', 'para': '热轧卷板'},
#             {'fut_code': 'ss', 'para': '不锈钢'}]
#     df = pd.DataFrame(data)
#     df.to_sql('FutCode', conn, index=True, if_exists='replace')
#     conn.close()
