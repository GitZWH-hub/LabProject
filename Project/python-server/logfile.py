#!/usr/bin/env python
# -*-coding:utf-8 -*-
"""
Logger模块
Created on Sept 27, 2021
@Author: zhangwh
"""
# 日志级别： debug < info < warning < error < critical
# logging.debug('debug级别，最低级别，一般开发人员用来打印一些调试信息')
# logging.info('info级别，正常输出信息，一般用来打印一些正常的操作')
# logging.warning('waring级别，一般用来打印警信息')
# logging.error('error级别，一般用来打印一些错误信息')
# logging.critical('critical 级别，一般用来打印一些致命的错误信息,等级最高')

import logging as log
from datetime import date


class Logger(object):
    def __init__(self):
        # print(" ====================== 初始化日志 ====================")
        self.today_date = date.today()
        log.basicConfig(filename='log/' + str(self.today_date) + '.log',
                        level=log.INFO,  # 控制台打印的日志级别
                        filemode='a',  # 'w'就是写模式，每次都会重新写日志，覆盖之前的日志; 'a'是追加模式，默认如果不写的话，就是追加模式
                        # format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s: %(message)s' # 全路径
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s'
                        )
