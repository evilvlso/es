#!/usr/bin/env python  
# -*- coding:utf-8 _*-  
""" 
@author: zhangslob 
@file: dingtalk.py 
@time: 2019/04/22
@desc: 
    钉钉机器人消息封装
"""

import requests


class DingtalkChatbot(object):

    def __init__(self, token='fa7140050dc761926e2555d81d157cbbaf9c6e09ff9844842ae112948bb1dbb2'):
        self.url = 'https://oapi.dingtalk.com/robot/send?access_token={}'.format(token)
        self.headers = {'Content-Type': 'application/json; charset=utf-8'}

    def send_msg(self, msg):
        data = {"msgtype": "text", "text": {'content': msg}}
        return self.post(data)

    def post(self, post_data):
        response = requests.post(self.url, headers=self.headers, json=post_data,
                                 timeout=10)
        data = response.json()
        if data['errmsg'] != 'ok':
            raise Exception('send msg error {}'.format(response.text))


if __name__ == '__main__':
    d = DingtalkChatbot('fa7140050dc761926e2555d81d157cbbaf9c6e09ff9844842ae112948bb1dbb2')
    d.send_msg('测试测试测试')
