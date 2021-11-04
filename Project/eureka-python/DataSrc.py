#!/usr/bin/env python
# -*-coding:utf-8 -*-
import json
import re

import tushare as ts
import sqlite3 as sql3

from pandas.core import frame

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
        return data


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

    # 获取某段时间内的所有交易日
    def getTradeDay(self, start, end):
        print("select cal_date from " + self.TABLENAME +
              " where is_open = '1' and cal_date between '" + start + "' and '" + end + "'")
        data = pd.read_sql_query("select cal_date from " + self.TABLENAME +
                                 " where is_open = '1' and cal_date between '" + start + "' and '" + end + "'", self.conn)
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

    def pullData(self, ts_code, start_date, end_date):
        log.info('-- 开始拉取历史行情(HisQuotes) --')
        try:
            data = self.pro.fut_daily(ts_code=ts_code, start_date=start_date, end_date=end_date)
            data.to_sql(ts_code[:2].upper(), self.conn, index=True, if_exists='append')
        except:
            log.error("to_sql ERROR")
        log.info('-- 拉取历史行情结束(HisQuotes) --')
        # print(data)
        return data

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

    # 用于回测（下载数据）功能，
    # 先查询库，若库中有需要的所有数据，则直接从库中查询。
    # 若库中数据不全，则from tushare and delete table data
    def getData(self, ts_code, start, end):
        self.pullData(ts_code=ts_code, start_date='20201001', end_date='20201001')
        # 库中获取数据
        data = self.sqlData(ts_code, start, end)

        if 0 == len(data):
            print("库中没有一条数据")
            pull = self.pullData(ts_code=ts_code, start_date=start, end_date=end)
            return pull

        with TradeCal() as tc:
            tradecal = tc.getTradeDay(start=start, end=end)

        # 库中存在完整数据
        if len(data) != len(tradecal):
            print("库中数据不完整")
            # 删除该库中所有该时间段的数据，并重新拉取tushare并append表
            self.deleteData(ts_code, start, end)
            data = self.pullData(ts_code, start, end)

        # 需要对data按日期拍下序
        data.sort_values(by="trade_date", ascending=True)
        print(data)
        # 添加两列，MAS：短期均线值，MAL长期均线值
        data['MAS'] = 0.0
        data['MAL'] = 0.0
        # 如果记录数大于4，需要计算均值返回，给前端显示,先计算5天的均值给前端显示试试
        data_length = len(data)
        if data_length >= 5:
            mas = mal = 0.0
            for i in range(data_length - 1, -1, -1):
                if i < data_length - 5:   # 第6天开始有前五日均值
                    data.loc[i, 'MAS'] = mas / 5
                    mas = mas - float(data.loc[i + 5, 'close'])
                if i < data_length - 10:  # 第十天开始有前10日均值
                    data.loc[i, 'MAL'] = mal / 10
                    mal = mal - float(data.loc[i + 10, 'close'])
                mas = mas + float(data.loc[i, 'close'])
                mal = mal + float(data.loc[i, 'close'])

                if i >= data_length - 5:
                    data.loc[i, 'MAS'] = mas / (data_length - i)
                if i >= data_length - 10:
                    data.loc[i, 'MAL'] = mal / (data_length - i)
                # print(mas)

        return data

    # sql查询，返回k线图字段，若无数据，则返回[]
    def sqlData(self, ts_code, start, end):
        data = []
        try:
            fut = ts_code[:2].upper()
            print("select trade_date,ts_code,open,close,high,low from " +
                  fut + " where ts_code = '" + ts_code.upper() + "' and trade_date between '" +
                  start + "' and '" + end + "'")
            data = pd.read_sql_query("select trade_date,ts_code,open,close,high,low from " +
                                     fut + " where ts_code = '" + ts_code.upper() + "' and trade_date between '"
                                     + start + "' and '" + end + "'",
                                     self.conn)
            print(data)
        except:
            log.info("ERROR")
        return data

    def deleteData(self, ts_code, start, end):
        try:
            fut = ts_code[:2].upper()
            print("delete from " + fut + " where ts_code = '" + ts_code.upper() +
                  "' and trade_date between '" + start + "' and '" + end + "'",)
            pd.read_sql_query("delete from " + fut + " where ts_code = '" + ts_code.upper() +
                              "' and trade_date between '" + start + "' and '" + end + "'", self.conn)
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