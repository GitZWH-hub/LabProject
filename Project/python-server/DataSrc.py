#!/usr/bin/env python
# -*-coding:utf-8 -*-
import json
import tushare as ts
import sqlite3 as sql3
from log.Logger import Logger
from datetime import datetime

logger = Logger()
'''
基类
Created on Sept 27, 2021    @Author: zwh
'''


class Base(object):
    def __init__(self):
        self.token = 'f0d2ecb5970c108c5959d1b445fb99e55690038748029204c0df86ec'
        self.pro = ts.pro_api(self.token)
        self.exchange = 'SHFE'
        self.DBNAME = 'DBData'

    def __enter__(self):
        self.conn = sql3.connect(self.DBNAME)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()

    def setExchange(self, exchange):
        self.exchange = exchange


'''
获取SHFE的期货合约信息: TuShare
Created on Sept 27, 2021    @Author: zhangwh
'''


class Futures(Base):
    def __enter__(self):
        super(Futures, self).__enter__()  # 【如果要继承父类的函数并重写，需要加一句: super(子类, self).函数名()】
        self.TABLENAME = 'Futures'
        return self

    def pull(self):
        logger.info('-- 开始拉取合约信息(Future) --')
        data = self.pro.fut_basic(exchange=self.exchange)
        try:  # index:是否插入索引，默认插入   if_exists:replace、append、fail
            data.to_sql(self.TABLENAME, self.conn, index=True, if_exists='replace')
        except:
            logger.error("to_sql ERROR")
        logger.info('-- 拉取合约信息结束(Future) --')

    def get_ts_code_by_date(self, start_year, end_year):
        ts_codes = pd.read_sql_query("select ts_code, fut_code from " + self.TABLENAME + " where last_ddate between '" +
                                     start_year + "' and '" + end_year + "'", self.conn)
        return ts_codes


'''
获取SHFE交易日历: TuShare
Created on Oct 5, 2021  @Author: zhangwh
'''


class TradeCal(Base):
    def __enter__(self):
        super(TradeCal, self).__enter__()
        self.TABLENAME = 'TradeCal'
        return self

    def pull(self, start_date, end_date):
        logger.info('-- 开始获取交易日历(TradeCal) --')
        try:
            data = self.pro.trade_cal(exchange=self.exchange, start_date=start_date, end_date=end_date)
            data.to_sql(self.TABLENAME, self.conn, index=True, if_exists='replace')
        except:
            logger.error('to_sql ERROR')
        logger.info('-- 拉取交易日历结束(TradeCal) --')

    # 获取某段时间内的所有交易日
    def getTradeDay(self, start, end):
        print("select cal_date from " + self.TABLENAME +
              " where is_open = '1' and cal_date between '" + start + "' and '" + end + "'")
        data = pd.read_sql_query("select cal_date from " + self.TABLENAME +
                                 " where is_open = '1' and cal_date between '" + start + "' and '" + end + "'",
                                 self.conn)
        return data


'''
获取SHFE历史行情信息: TuShare
Created on Oct 5, 2021  @Author: zhangwh
'''


class HisQuotes(Base):
    def __enter__(self):
        super(HisQuotes, self).__enter__()
        self.TABLENAME = 'HisQuotes'
        return self

    def pull(self, start_date, end_date, ts_code=None):
        logger.info('-- 开始拉取历史行情(HisQuotes) --')
        data = []
        try:
            with Futures() as future:
                if ts_code is None:
                    # 查询期货合约信息表,查询时间区间内的所有合约代码，全拉下来
                    df = future.get_ts_code_by_date(start_date, end_date)
                    logger.info("正在拉取{}个合约的历史行情".format(len(df)))
                    count = 0
                    for i, r in df.iterrows():
                        count += 1
                        print('\r' + str(count) + '/' + str(len(df)), end='', flush=True)
                        data = self.pro.fut_daily(ts_code=r['ts_code'])
                        data.to_sql(r['fut_code'].upper(), self.conn, index=True, if_exists='replace')
                else:
                    data = self.pro.fut_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
                    data.to_sql(ts_code[:2].upper(), self.conn, index=True, if_exists='append')
        except:
            logger.error("to_sql ERROR")
        logger.info('-- 拉取历史行情结束(HisQuotes) --')
        return data

    # 用于回测（下载数据）功能，
    # 先查询库，若库中有需要的所有数据，则直接从库中查询。
    # 若库中数据不全，则from tushare and delete table data
    def getData(self, ts_code, start, end):
        self.pull(start_date='20201001', end_date='20201001', ts_code=ts_code)
        # 库中获取数据
        data = self.sqlData(ts_code, start, end)

        if 0 == len(data):
            logger.info("库中没有一条数据")
            pull = self.pull(start_date=start, end_date=end, ts_code=ts_code)
            return pull

        with TradeCal() as tc:
            tradecal = tc.getTradeDay(start=start, end=end)

        # 库中不存在完整数据
        if len(data) != len(tradecal):
            logger.info("库中数据不完整")
            # 删除该库中所有该时间段的数据，并重新拉取tushare并append表
            self.deleteData(ts_code, start, end)
            data = self.pull(start, end, ts_code)

        # 需要对data按日期拍下序
        data = data.sort_values(by="trade_date", ascending=True)
        # 添加两列，MAS：短期均线值，MAL长期均线值
        # 这里当天的五日均线，包含了当天的结算价（后续需要确定五日均线是否是包含当日，按理说应该是包含的，结算价就是当日的平均价）
        data['MAS'] = round(data.close.rolling(5, min_periods=1).mean(), 2)
        data['MAL'] = round(data.close.rolling(10, min_periods=1).mean(), 2)
        # 再查询库中的相关数据，并计算均价放到返回的数据data中（因为前4天的五日均价无法通过当前的data得来）
        # 暂时先不实现。。。。。
        return data

    # sql查询，返回k线图字段，若无数据，则返回[]
    def sqlData(self, ts_code, start, end):
        data = []
        try:
            fut = ts_code[:2].upper()
            logger.debug("select trade_date,ts_code,open,close,high,low,vol from " + fut + " where ts_code = '" +
                         ts_code.upper() + "' and trade_date between '" + start + "' and '" + end + "'")
            data = pd.read_sql_query(
                "select trade_date,ts_code,open,close,high,low,vol from " + fut + " where ts_code = '"
                + ts_code.upper() + "' and trade_date between '" + start + "' and '" + end + "'",
                self.conn)
        except:
            logger.error("to sql ERROR")
        return data

    def deleteData(self, ts_code, start, end):
        try:
            fut = ts_code[:2].upper()
            logger.debug("delete from " + fut + " where ts_code = '" + ts_code.upper() +
                         "' and trade_date between '" + start + "' and '" + end + "'", )
            pd.read_sql_query("delete from " + fut + " where ts_code = '" + ts_code.upper() +
                              "' and trade_date between '" + start + "' and '" + end + "'", self.conn)
        except:
            logger.info("to sql ERROR")


'''
获取SHFE结算参数: TuShare
Created on Oct 5, 2021  @Author: zhangwh
'''


class FutSettle(Base):
    def __enter__(self):
        super(FutSettle, self).__enter__()
        self.TABLENAME = 'FutSettle'
        return self

    def pull(self, start_date=None, end_date=None):
        logger.info('-- 开始获取结算参数(FutSettle)')
        try:
            # fut_settle接口中，ts_code和trade_date至少需要一个
            # data = self.pro.fut_settle(trade_date=trade_date, ts_code=ts_code, exchange=self.exchange)
            data = self.pro.fut_settle(exchange=self.exchange, start_date=start_date, end_date=end_date)
            data.to_sql(self.TABLENAME, self.conn, index=True, if_exists='replace')
        except:
            logger.error('to_sql ERROR')
        logger.info('-- 拉取结算参数结束(FutSettle) --')


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
            logger.error("sql error")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()
