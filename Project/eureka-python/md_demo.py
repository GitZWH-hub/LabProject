# -*- coding: utf-8 -*-

import thostmduserapi as mdapi
import csv
import os
from pathlib import Path
from datetime import datetime
import requests
import json

'''
以下为需要订阅行情的合约号，注意选择有效合约；
有效连上但没有行情可能是过期合约或者不在交易时间内导致
'''


# 将实时行情存到csv文件,目前测试阶段仅存取cu2110和cu2111的数据
# 设想：在交易时间结束后，将csv文件数据更新到 其他pyton服务使用库:DBData中，则在下一个交易日时，属于历史数据了
# （转存：读取csv并存库的程序待定）

class CFtdcMdSpi(mdapi.CThostFtdcMdSpi):

    def __init__(self, tapi, subID):
        mdapi.CThostFtdcMdSpi.__init__(self)
        self.tapi = tapi
        self.csvfiles = {}
        self.submap = {}
        self.date = datetime.strftime(datetime.now(), '%Y%m%d')
        self.__create()
        self.subID = subID
        self.url = "http://localhost:5678/sendQuotes"
        self.headers = {'Content-type': 'application/json'}

    def __create(self):
        b = os.getcwd()
        myfile = Path(b + '/csv/' + self.date)
        if myfile.exists() is False:
            os.mkdir(b + "/csv/" + self.date)

    def __openCsv(self):
        csvheader = (
            ["TradingDay", "InstrumentID", "LastPrice", "PreSettlementPrice", "PreClosePrice", "PreOpenInterest",
             "OpenPrice", "HighestPrice", "LowestPrice", "Volume", "Turnover", "OpenInterest", "ClosePrice",
             "SettlementPrice", "UpperLimitPrice", "LowerLimitPrice", "PreDelta", "CurrDelta", "UpdateTime",
             "UpdateMillisec", "BidPrice1", "BidVolume1", "AskPrice1", "AskVolume1", "AveragePrice", "ActionDay",
             "BidPrice2", "BidVolume2", "AskPrice2", "AskVolume2", "BidPrice3", "BidVolume3", "AskPrice3", "AskVolume3",
             "BidPrice4", "BidVolume4", "AskPrice4", "AskVolume4", "BidPrice5", "BidVolume5", "AskPrice5",
             "AskVolume5"])

        # 如果该合约行情文件不存在，则创建并写入头
        for id in self.subID:
            csvname = "csv/" + str(self.date) + f"/{id}.csv"
            print(id)
            csvfile = open(csvname, 'w', newline='')
            csvfile_w = csv.writer(csvfile)
            if not os.path.isfile(csvname):
                print("不存在csv文件，写入head")
                csvfile_w.writerow(csvheader)
            self.csvfiles[id] = csvfile
            self.submap[id] = csvfile_w

    def OnFrontConnected(self) -> "void":
        print("OnFrontConnected")
        loginfield = mdapi.CThostFtdcReqUserLoginField()
        loginfield.BrokerID = "9999"
        loginfield.UserID = "192643"
        loginfield.Password = "Zhangweihua3706!"
        loginfield.UserProductInfo = "python dll"
        self.tapi.ReqUserLogin(loginfield, 0)
        self.__openCsv()

    def OnRspUserLogin(self, pRspUserLogin: 'CThostFtdcRspUserLoginField', pRspInfo: 'CThostFtdcRspInfoField',
                       nRequestID: 'int', bIsLast: 'bool') -> "void":
        print(
            f"OnRspUserLogin, SessionID={pRspUserLogin.SessionID},ErrorID={pRspInfo.ErrorID},ErrorMsg={pRspInfo.ErrorMsg}")
        ret = self.tapi.SubscribeMarketData([id.encode('utf-8') for id in self.subID], len(self.subID))
        print(nRequestID)

    # 深度行情通知,当SubscribeMarketData订阅行情后,行情通知由此推送
    def OnRtnDepthMarketData(self, pDepthMarketData: 'CThostFtdcDepthMarketDataField') -> "void":
        mdlist = ([pDepthMarketData.TradingDay, pDepthMarketData.InstrumentID, pDepthMarketData.LastPrice,
                   pDepthMarketData.PreSettlementPrice, pDepthMarketData.PreClosePrice,
                   pDepthMarketData.PreOpenInterest,
                   pDepthMarketData.OpenPrice, pDepthMarketData.HighestPrice, pDepthMarketData.LowestPrice,
                   pDepthMarketData.Volume, pDepthMarketData.Turnover, pDepthMarketData.OpenInterest,
                   pDepthMarketData.ClosePrice, pDepthMarketData.SettlementPrice, pDepthMarketData.UpperLimitPrice,
                   pDepthMarketData.LowerLimitPrice, pDepthMarketData.PreDelta, pDepthMarketData.CurrDelta,
                   pDepthMarketData.UpdateTime, pDepthMarketData.UpdateMillisec, pDepthMarketData.AveragePrice,
                   pDepthMarketData.ActionDay,
                   pDepthMarketData.BidPrice1, pDepthMarketData.BidVolume1, pDepthMarketData.AskPrice1,
                   pDepthMarketData.AskVolume1,
                   pDepthMarketData.BidPrice2, pDepthMarketData.BidVolume2, pDepthMarketData.AskPrice2,
                   pDepthMarketData.AskVolume2,
                   pDepthMarketData.BidPrice3, pDepthMarketData.BidVolume3, pDepthMarketData.AskPrice3,
                   pDepthMarketData.AskVolume3,
                   pDepthMarketData.BidPrice4, pDepthMarketData.BidVolume4, pDepthMarketData.AskPrice4,
                   pDepthMarketData.AskVolume4,
                   pDepthMarketData.BidPrice5, pDepthMarketData.BidVolume5, pDepthMarketData.AskPrice5,
                   pDepthMarketData.AskVolume5])

        print(mdlist)
        re = {'tradingDay': pDepthMarketData.TradingDay, 'instrumentID': pDepthMarketData.InstrumentID,
              'lastPrice': pDepthMarketData.LastPrice, 'preSettlementPrice': pDepthMarketData.PreSettlementPrice,
              'preClosePrice': pDepthMarketData.PreClosePrice, 'preOpenInterest': pDepthMarketData.PreOpenInterest,
              'openPrice': pDepthMarketData.OpenPrice, 'highestPrice': pDepthMarketData.HighestPrice,
              'lowestPrice': pDepthMarketData.LowestPrice, 'volume': pDepthMarketData.Volume,
              'turnover': pDepthMarketData.Turnover, 'openInterest': pDepthMarketData.OpenInterest,
              'closePrice': pDepthMarketData.ClosePrice, 'settlementPrice': pDepthMarketData.SettlementPrice,
              'upperLimitPrice': pDepthMarketData.UpperLimitPrice, 'lowerLimitPrice': pDepthMarketData.LowerLimitPrice,
              'preDelta': pDepthMarketData.PreDelta, 'currDelta': pDepthMarketData.CurrDelta,
              'updateTime': pDepthMarketData.UpdateTime, 'updateMillisec': pDepthMarketData.UpdateMillisec,
              'averagePrice': pDepthMarketData.AveragePrice, 'actionDay': pDepthMarketData.ActionDay,
              'bidPrice1': pDepthMarketData.BidPrice1, 'bidVolume1': pDepthMarketData.BidVolume1,
              'askPrice1': pDepthMarketData.AskPrice1, 'askVolume1': pDepthMarketData.AskVolume1,
              'bidPrice2': pDepthMarketData.BidPrice2, 'bidVolume2': pDepthMarketData.BidVolume2,
              'askPrice2': pDepthMarketData.AskPrice2, 'askVolume2': pDepthMarketData.AskVolume2,
              'bidPrice3': pDepthMarketData.BidPrice3, 'bidVolume3': pDepthMarketData.BidVolume3,
              'askPrice3': pDepthMarketData.AskPrice3, 'askVolume3': pDepthMarketData.AskVolume3,
              'bidPrice4': pDepthMarketData.BidPrice4, 'bidVolume4': pDepthMarketData.BidVolume4,
              'askPrice4': pDepthMarketData.AskPrice4, 'askVolume4': pDepthMarketData.AskVolume4,
              'bidPrice5': pDepthMarketData.BidPrice5, 'bidVolume5': pDepthMarketData.BidVolume5,
              'askPrice5': pDepthMarketData.AskPrice5, 'askVolume5': pDepthMarketData.AskVolume5
              }

        # 这里应该再链接java服务发送给前台显示
        response = requests.post(self.url, data=json.dumps(re), headers=self.headers)

        self.submap[pDepthMarketData.InstrumentID].writerow(mdlist)
        self.csvfiles[pDepthMarketData.InstrumentID].flush()

    def OnRspSubMarketData(self, pSpecificInstrument: 'CThostFtdcSpecificInstrumentField',
                           pRspInfo: 'CThostFtdcRspInfoField', nRequestID: 'int', bIsLast: 'bool') -> "void":
        print("OnRspSubMarketData")
        print("InstrumentID=", pSpecificInstrument.InstrumentID)
        print("ErrorID=", pRspInfo.ErrorID)
        print("ErrorMsg=", pRspInfo.ErrorMsg)

    def OnRspUserLogout(self, pUserLogout: "CThostFtdcUserLogoutField", pRspInfo: "CThostFtdcRspInfoField",
                        nRequestID: "int", bIsLast: "bool") -> "void":
        print("用户已登出")
        print("CThostFtdcUserLogoutField")


class Controller(object):

    def __init__(self):
        self.mduserapi = None
        # 默认 7 * 24环境
        self.url = "tcp://180.168.146.187:10131"
        self.subID = []

    # 开始订阅行情
    def start(self):
        if self.mduserapi is None:
            self.mduserapi = mdapi.CThostFtdcMdApi_CreateFtdcMdApi()
            self.mduserspi = CFtdcMdSpi(self.mduserapi, self.subID)
            self.mduserapi.RegisterFront(self.url)
            self.mduserapi.RegisterSpi(self.mduserspi)
            self.mduserapi.Init()
            self.mduserapi.Join()

    # 停止订阅
    def stop(self):
        if self.mduserapi is not None:
            self.mduserapi.RegisterSpi(None)
            self.mduserapi = None

    def setEV(self, flag):
        if flag == 1 or flag == '1':
            self.url = "tcp://101.230.209.178:53313"
            print("交易环境")
            # "tcp://180.168.146.187:10212"
        else:
            self.url = "tcp://180.168.146.187:10131"
            print("7*24环境")

    def addFutCode(self, fut_code):
        # 先判断subID里有无此合约
        if fut_code not in self.subID:
            self.subID.append(fut_code)
        print("此时订阅合约有：")
        print(self.subID)

    def addSubscribe(self, fut_code):
        # self.mduserapi.÷
        pass
