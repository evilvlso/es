#!/usr/bin/env python  
# -*- coding:utf-8 _*-  
""" 
@author: zhangslob 
@file: items_.py 
@time: 2019/04/24
@desc: 
    
"""
import scrapy


class HtmlItem(scrapy.Item):
    html = scrapy.Field()
    url = scrapy.Field()
    save_time = scrapy.Field()
    callback_ = scrapy.Field()
    request = scrapy.Field()
    version = scrapy.Field()
    created_time = scrapy.Field()
    created_time_ts = scrapy.Field()
