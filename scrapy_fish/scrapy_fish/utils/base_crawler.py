#!/usr/bin/env python  
# -*- coding:utf-8 _*-  
""" 
@author: zhangslob 
@file: base_crawler.py 
@time: 2019/04/17
@desc: 
    
"""
import json
import scrapy
import threading

from .rabbit_manager import mq_main

from scrapy.spiders import CrawlSpider as CS
from scrapy.spiders import Spider as SD

from scrapy_redis.spiders import RedisCrawlSpider as RCS
from scrapy_redis.spiders import RedisSpider as RSD


class BaseSpider(object):

    def __init__(self, *args, **kwargs):
        import logging
        logger = logging.getLogger('pika')
        logger.setLevel(logging.WARNING)

        def to_json(response):
            return json.loads(response.text)

        def retry_(response, retry_times=15):
            meta = response.meta
            times_ = meta.get('cus_retry_times', 0) + 1

            if times_ == -1:
                # 无限重试
                retires = response.request.copy()
                retires.meta['cus_retry_times'] = times_
                retires.dont_filter = True
                retires.priority = 10

                self.logger.debug('retry times: {}, {}'.format(times_, response.url))
                return retires

            if times_ < retry_times:
                retires = response.request.copy()
                retires.meta['cus_retry_times'] = times_
                retires.dont_filter = True
                retires.priority = 10

                self.logger.debug('retry times: {}, {}'.format(times_, response.url))
                return retires
            else:
                self.logger.info('retry times: {} too many {}'.format(times_, response.url))
                return None

        scrapy.http.Response.json = to_json     # json loads
        scrapy.http.Response.retry = retry_     # 自定义重试

        assert not self.__dict__.get('custom_settings'), "请设置custom_settings"

        # self.t = threading.Thread(target=mq_main, args=(self.name, self.logger))
        # self.t.setDaemon(True)
        # self.t.start()


class CrawlSpider(BaseSpider, CS):
    def __init__(self, *args, **kwargs):
        BaseSpider.__init__(self, *args, **kwargs)
        CS.__init__(self, *args, **kwargs)


class CrawlSpiderRedis(BaseSpider, RCS):

    def __init__(self, *args, **kwargs):
        BaseSpider.__init__(self, *args, **kwargs)
        RCS.__init__(self, *args, **kwargs)


class Spider(BaseSpider, SD):

    def __init__(self, *args, **kwargs):
        BaseSpider.__init__(self, *args, **kwargs)
        SD.__init__(self, *args, **kwargs)


class SpiderRedis(BaseSpider, RSD):

    def __init__(self, *args, **kwargs):
        BaseSpider.__init__(self, *args, **kwargs)
        RSD.__init__(self, *args, **kwargs)



