#!/usr/bin/env python  
# -*- coding:utf-8 _*-  
""" 
@author: zhangslob 
@file: spider_settings.py 
@time: 2019/04/22
@desc: 
    
"""
import collections

from ..settings import *
from scrapy.utils.project import get_project_settings

project_settings = get_project_settings()


class CustomSettings(object):
    """
    使用方法
    c = CustomSettings()
    c.DOWNLOAD_TIMEOUT_CUS = 10
    custom_settings = c()
    """
    def __init__(self):
        self.spider_name = project_settings['BOT_NAME']

        self.ROBOTSTXT_OBEY_CUS = False

        self.ITEM_PIPELINES_CUS = {}
        self.SPIDER_MIDDLEWARES_CUS = {}
        self.DOWNLOADER_MIDDLEWARES_CUS = {}
        self.EXTENSIONS_CUS = {}

        self.DOWNLOAD_DELAY_CUS = 'defeat'
        self.CONCURRENT_REQUESTS_PER_DOMAIN_CUS = 16
        self.CONCURRENT_REQUESTS_PER_IP_CUS = 16
        self.CONCURRENT_REQUESTS_CUS = 16
        self.DOWNLOAD_TIMEOUT_CUS = 10
        self.TIMEOUT_CUS = 10

        self.COOKIES_ENABLED_CUS = 'defeat'
        self.COOKIES_DEBUG_CUS = 'defeat'

        self.RETRY_ENABLED_CUS = 'defeat'
        self.RETRY_HTTP_CODES_CUS = 'defeat'
        self.RETRY_TIMES_CUS = 16
        self.RETRY_PRIORITY_ADJUST_CUS = 'defeat'

        self.SCHEDULER_CUS = 'defeat'
        self.DUPEFILTER_CLASS_CUS = 'defeat'
        self.REDIS_START_URLS_AS_SET_CUS = True
        self.SCHEDULER_QUEUE_CLASS_CUS = 'defeat'
        self.REDIS_ITEMS_KEY_CUS = 'defeat'
        self.REDIS_ITEMS_SERIALIZER_CUS = 'defeat'
        self.REDIS_START_URLS_KEY_CUS = 'defeat'
        self.SCHEDULER_IDLE_BEFORE_CLOSE_CUS = 'defeat'
        self.SCHEDULER_PERSIST_CUS = 'defeat'

        self.EnProxy = False
        self.EnRedis = False

        self.LOG_LEVEL_CUS = 'DEBUG'
        self.LOG_FILE_CUS = ''

        self.EnSaveHtml = True
        self.SAVE_HTML_DB_CUS = None

        self.EnFakeUserAgent = True
        self.RANDOM_UA_TYPE_CUS = ''

        self.DOWNLOAD_FAIL_ON_DATALOSS_CUS = False

    def __call__(self, *args, **kwargs):

        # 启用分布式
        if self.EnRedis:
            self.SCHEDULER_CUS = "scrapy_redis.scheduler.Scheduler"
            self.DUPEFILTER_CLASS_CUS = "scrapy_redis.dupefilter.RFPDupeFilter"

        # 启用代理
        if self.EnProxy:
            self.DOWNLOADER_MIDDLEWARES_CUS.update({
                "{}.utils.middlewares_.ProxyMiddleware".format(self.spider_name): 520
            })

        # 储存原始html管道
        if self.EnSaveHtml:
            self.ITEM_PIPELINES_CUS.update({
                "{}.utils.pipelines_.SaveHtmlPipeline".format(self.spider_name): 200
            })

        # 随机头，注意都是PC端
        if self.EnFakeUserAgent:
            self.DOWNLOADER_MIDDLEWARES_CUS.update({
                "{}.utils.middlewares_.UAMiddleware".format(self.spider_name): 521
            })

        self.ITEM_PIPELINES_CUS.update({
            "{}.utils.pipelines_.AddTime".format(self.spider_name): 100,  # 增加爬虫抓取时间
            "{}.utils.pipelines_.DropItemLogPipeline".format(self.spider_name): 1000,  # 抛弃item的输出日志
        })

        result = dict()

        for key_, value_ in self.__dict__.items():

            # 过滤出相关属性
            if key_.endswith('_CUS') or key_.startswith('En'):

                key_ = key_.replace('_CUS', '')
                default = globals().get(key_)

                if isinstance(default, dict):
                    # 和默认配置合并
                    result[key_] = default.copy()
                    result[key_].update(value_)
                elif key_.startswith('En'):
                    result[key_] = value_
                elif value_ == 'defeat':
                    pass
                else:
                    result[key_] = value_

        return result


class PersistenceDict(collections.UserDict):

    def __init__(self, *args, **kwargs):
        super(PersistenceDict, self).__init__(*args, **kwargs)
        self.mongodb_client = mongo_client()
        self.db = None
        self.coll = None
        self.table_name = None
        self.spider_name = None

    def connection(self, spider_name, db_name=None):
        self.db = self.mongodb_client.get_database()
        self.data['spider_name'] = spider_name
        self.spider_name = spider_name
        self.coll = self.db['{}_conf'.format(spider_name)]
        # self.table_name = '{}_conf'.format(spider_name)
        # self._coll = self.coll[self.table_name]

        # 获取相关数据
        d = self.coll.find_one({'spider_name': spider_name}, {'_id': 0}) or {}
        self.data.update(d)

    def __setitem__(self, key, value):
        super(PersistenceDict, self).__setitem__(key, value)
        self.coll.update({'spider_name': self.spider_name}, {'$set': self.data}, upsert=True)

    def __getitem__(self, item):
        self.flush()
        return super(PersistenceDict, self).__getitem__(item)

    def flush(self):
        d = self.coll.find_one({'spider_name': self.spider_name}, {'_id': 0}) or {}
        self.data.update(d)










