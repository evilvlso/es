#!/usr/bin/env python  
# -*- coding:utf-8 _*-  
""" 
@author: zhangslob 
@file: date_.py 
@time: 2019/04/24
@desc: 
    常用时间
"""  

import time
import datetime
import pytz

tz = pytz.timezone('Asia/Shanghai')

t = datetime.datetime.fromtimestamp(int(time.time()), pytz.timezone('Asia/Shanghai'))


def get_date():
    """
    :return: 2019_05_05
    """
    return t.strftime('%Y_%m_%d')


def get_hour():
    """
    :return: 2019_05_05 14
    """
    return t.strftime('%Y_%m_%d %H')


def get_minute():
    """
    :return: 2019_05_05 14:11
    """
    return t.strftime('%Y_%m_%d %H:%M')


def get_second():
    """
    :return: 2019-05-05 14:11:50
    """
    return t.strftime('%Y-%m-%d %H:%M:%S')
