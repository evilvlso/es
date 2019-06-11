#!/usr/bin/env python  
# -*- coding:utf-8 _*-  
""" 
@author: zhangslob 
@file: middlewares_.py 
@time: 2019/04/22
@desc: 
    
"""  

import base64
import random

from .ua_list import user_agent

# 代理服务器
proxyServer = "http://http-dyn.abuyun.com:9020"

# 代理隧道验证信息
proxyUser = "H5T13T79VO8E385D"
proxyPass = "6D764ADAE38AB54D"

proxyAuth = "Basic " + base64.urlsafe_b64encode(bytes((proxyUser + ":" + proxyPass), "ascii")).decode("utf8")


class ProxyMiddleware(object):

    def process_request(self, request, spider):
        request.meta["proxy"] = proxyServer
        request.headers["Proxy-Authorization"] = proxyAuth


class UAMiddleware(object):

    def process_request(self, request, spider):
        request.headers['User-Agent'] = random.choice(user_agent)
