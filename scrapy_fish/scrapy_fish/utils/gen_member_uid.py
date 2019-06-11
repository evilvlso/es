#!/usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
@author: zhangslob 
@file: gen_member_uid.py 
@time: 2019/05/06
@desc: 
    
"""

import time
from .settings_ import *


class CheckLeft(object):
    def __init__(self, status, tmp_num, data, logger):
        self.redis = redis_client()
        self.mongo = mongo_client()
        self.status = status
        self.tmp_num = tmp_num
        self.data = data
        self.logger = logger

    def watch_uid_num(self):
        """
        检测redis中的数量
        :return: bool
        """
        redis_key = '{}:start_urls'.format(self.status)
        num_ = self.redis.scard(redis_key)
        if num_ > 20000:
            return False
        else:
            return True

    def gen_uid(self):
        """
        ID生成器
        :return: 生成器
        """
        if self.status == 'all_goods':
            while True:
                js = 0
                result = list()
                while js < 20000:
                    # num1 = self.tmp_num
                    # self.tmp_num += 10000
                    # num_id = random.randint(num1, self.tmp_num)
                    # js += 1
                    # result.append(num_id)
                    js += 1
                    self.tmp_num += 1
                    result.append(self.tmp_num)
                yield result

    def main_(self):
        self.logger.info('main_ {}'.format(self.tmp_num))
        while True:
            if self.watch_uid_num():
                uid_list = next(self.gen_uid())
                redis_key = '{}:start_urls'.format(self.status)
                if uid_list:
                    self.logger.info('get uid_list {}'.format(uid_list[0]))
                    self.redis.sadd(redis_key, *uid_list)
                    self.logger.info('gen_member_uid main_ with: {}'.format(self.tmp_num))
            self.data['uid_num'] = self.tmp_num
            time.sleep(3)

