#!/usr/bin/env python  
# -*- coding:utf-8 _*-  
""" 
@author: zhangslob 
@file: spiders.py 
@time: 2019/04/24
@desc: 
    爬虫示例文件
"""
import json
from urllib.parse import urlencode

import scrapy

from ..items import CategoryItem, DetailItem
from ..utils.base_crawler import SpiderRedis
from ..utils.tools.dingtalk import DingtalkChatbot
from ..utils.spider_settings import CustomSettings


class ExampleSpider(SpiderRedis):
    name = 'mryitao'
    # start_urls = ['https://www.baidu.com/']

    c = CustomSettings()
    c.EnProxy = True
    c.EnRedis = True
    c.EnSaveHtml = False
    c.EnFakeUserAgent = False
    c.LOG_LEVEL_CUS = 'INFO'
    c.RETRY_TIMES_CUS = 15
    c.DOWNLOAD_TIMEOUT_CUS = 20
    c.COOKIES_ENABLED_CUS = False
    c.CONCURRENT_REQUESTS_CUS = 100
    c.CONCURRENT_REQUESTS_PER_DOMAIN_CUS = 100
    c.CONCURRENT_REQUESTS_PER_IP_CUS = 100
    c.REDIS_START_URLS_AS_SET_CUS = True
    c.CONCURRENT_ITEMS_CUS = 200
    c.RETRY_HTTP_CODES_CUS = list(range(400, 600))
    #
    c.DEFAULT_REQUEST_HEADERS_CUS = {
        'Host': 'api.mryitao.cn',
        'accept': '*/*',
        'content-type': 'application/json;charset=UTF-8',
        'accept-language': 'zh-cn',
        'user-agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16A366 MicroMessenger/7.0.3(0x17000321) NetType/WIFI Language/zh_CN',
        'referer': 'https://servicewechat.com/wxeb45228be3146ddc/90/page-frame.html',
    }

    c.ITEM_PIPELINES_CUS = {
        'scrapy_fish.pipelines.MongoDbPipeline': 300,
        'scrapy_fish.utils.pipelines_.MySQLPipeline': 301,
        'scrapy_fish.utils.pipelines_.MysqlESPipeline': 299,
    }
    custom_settings = c()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ding = DingtalkChatbot()
        self.category1_url = 'https://api.mryitao.cn/api/marketing/classification/firstList'
        self.category2_url = 'https://api.mryitao.cn/api/marketing/classification/secondList'
        self.items_url = 'https://api.mryitao.cn/api/marketing/classification/getClassifyProductList'
        self.sku_url = 'https://api.mryitao.cn/api/product/v4/productDetail'

    def make_request_from_data(self, data):
        """
        接受MQ消息，推送到redis，再从redis中取命令
        :param data:
        :return:
        """
        task = json.loads(data)
        meta = task.get("meta")
        if task['operate'] == 'get_categories':
            self.logger.info("the task of get_categories. ")
            params = self.gen_common_params()
            url = "?".join((self.category1_url, params))
            return scrapy.Request(url, callback=self.parse_category1
                                  , dont_filter=True, method="POST")

        if task['operate'] == 'get_product_by_sku':
            spu_id = meta['spu_id']
            meta['category3_id'] = meta['category_code']
            meta['category1_name'] = meta['category_one']
            meta['category2_name'] = meta['category_two']
            meta["operate"] = 'get_product_by_sku'
            params = self.gen_common_params()
            url = "?".join((self.sku_url, params))
            data = {"sku": "{}".format(spu_id), "address": None}
            self.logger.info("the task of get_product_by_sku %s "%(spu_id,))
            return scrapy.Request(url=url, method="POST", callback=self.parse_sku,
                                  body=json.dumps(data), dont_filter=True, meta=meta)

    def parse_category1(self, response):
        data = response.json()
        signal = data.get("code") == 0
        if signal:
            category1_list = []
            categorydata = data.get("data", {}).get("lists", [])
            for category in categorydata:
                meta = {}
                category1_name = category.get("name", "")
                category1_id = category.get("id", "")
                meta["category1_name"] = category1_name
                meta["category1_id"] = category1_id
                meta["operate"] = "get_categories"
                if category1_id:
                    category_temp = self.gen_category_temp(category_name=category1_name, category_id=category1_id,
                                                           level=1)
                    category_temp.pop("source_pid")
                    category1_list.append(category_temp)
                    params = self.gen_common_params()
                    url = "?".join((self.category2_url, params))
                    data = {"firstId": category1_id}
                    yield scrapy.Request(url=url, callback=self.parse_category2, body=json.dumps(data),
                                         dont_filter=True, method="POST", meta=meta)
            yield {"_id": category1_id, "data": category1_list, "site_name": self.name, "operate": "get_categories"}
        else:
            self.logger.error("一级分类目录API请求错误: %s" % (data,))

    def parse_category2(self, response):
        """
        处理二级分类 三级分类
        :param response:
        :return:
        """
        data = response.json()
        signal = data.get("code") == 0
        if signal:
            meta = response.meta
            category2_and_3_list = []
            category2_infos = data.get("data", {}).get("lists", [])
            for category2_info in category2_infos:
                category2_id = category2_info.get("id", "")
                category2_name = category2_info.get("name", "")
                category1_id = meta.get("category1_id")
                category_temp = self.gen_category_temp(category_name=category2_name, category_id=category2_id, level=2,
                                                       parent_category_id=category1_id)
                cbindcatelogids = category2_info.get("bindCatelogIds", "")  # 请求所需参数
                category2_and_3_list.append(category_temp)
                meta["category2_id"] = category2_id
                meta["category2_name"] = category2_name
                meta["cbindcatelogids"] = cbindcatelogids
                params = self.gen_common_params()
                url = "?".join((self.items_url, params))
                data = {"pageNo": 0, "pageSize": 50, "bindCatelogIds": cbindcatelogids,
                        "secondId": "%s" % (category2_id,)}
                yield scrapy.Request(url, method="POST", callback=self.parse_items, dont_filter=True,
                                     body=json.dumps(data), meta=meta)
            # 二三级分类入库
            if category2_and_3_list:
                category_item = CategoryItem()
                category_item["data"] = category2_and_3_list
                category_item["_id"] = category2_id
                category_item["site_name"] = self.name
                category_item["operate"] = "get_categories"
                yield category_item
        else:
            self.logger.error("二级分类目录API请求错误: %s" % (data,))
            pass

    def parse_items(self, response):
        """
        处理商品列表 换页
        :param response:
        :return:
        """
        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            # self.logger.error("items json 解析错误 : %s" % (response.text,))
            yield response.retry()
        else:
            signal = data.get("code") == 0
            if signal:
                meta = response.meta
                # ->sku
                items = data.get("data", {}).get("productList", [])
                page = meta.get("page", 0)
                if items:
                    self.logger.debug("category2:[%s],page:[%s],items:[%s]" % (meta.get("category2_id"), page, len(items)))
                    for item in items:
                        sku = item.get("productInfo").get("sku", "")
                        meta["operate"] = "get_product_by_category"
                        params = self.gen_common_params()
                        url = "?".join((self.sku_url, params))
                        payload = {"sku": "{}".format(sku), "address": None}
                        yield scrapy.Request(url=url, method="POST", callback=self.parse_sku,
                                             body=json.dumps(payload), dont_filter=True, meta=meta)
                    # -> next page
                    hasmore = data.get("data", {}).get("hasMore")
                    if hasmore:
                        meta["page"] = page + 1
                        params = self.gen_common_params()
                        url = "?".join((self.items_url, params))
                        data = {"pageNo": page + 1, "pageSize": 50, "bindCatelogIds": meta.get("cbindcatelogids"),
                                "secondId": "%s" % (meta.get("category2_id"),)}
                        yield scrapy.Request(url, method="POST", callback=self.parse_items, dont_filter=True,
                                             body=json.dumps(data), meta=meta)
            else:
                self.logger.error("商品列表API请求错误: %s" % (data,))

    def parse_sku(self, response):
        """
        处理sku信息
        :param response:
        :return:
        """
        try:
            data = response.json()
        except json.decoder.JSONDecodeError:
            # self.logger.debug("sku json 解析错误 : %s" % (response.text,))
            yield response.retry()
        else:
            signal = data.get("code") == 0
            if signal:
                meta = response.meta
                data = data.get("data", {})
                sku_list_info = data.get("spec", [])
                status = data.get("label")
                if status == 0 and sku_list_info:
                    self.logger.debug("category2:[%s],sku_len:[%s]" % (meta.get("category2_id"), len(sku_list_info)))
                    sku_list = []
                    for spec in sku_list_info:
                        info = dict(
                            sku_id=''.join(spec.get("specIds", [])),
                            spu_id=spec.get("sku"),
                            origin_price=spec.get("originalPrice") / 100,
                            discount_price=spec.get("discountPrice") / 100,
                            # quantity=v.get("stockCount"),
                            spec=spec.get("spec").replace("'", "").replace('"', ""),
                            site_name=self.name
                        )
                        sku_list.append(info)
                    spu_info = {
                        'category_code': meta.get("category2_id", ""),
                        'spu_id': data.get("sku", ""),
                        'default_sku_id': sku_list[0]['sku_id'],  # the first sku
                        # 'upc_code': None,
                        'title': data.get("productName").replace("'", "").replace('"', ""),
                        'site_name': self.name,
                        'feature': data.get("desc", "").replace("'", "").replace('"', ""),
                        # 'payoff': None,
                        'status': status,
                        "category_one": meta.get("category1_name", ""),
                        "category_two": meta.get("category2_name", ""),
                    }
                    if data.get("productNameTag", ""):
                        spu_info["brand"] = data.get("productNameTag", "")
                    detail = DetailItem()
                    detail["_id"] = meta.get("spu_id", "")
                    detail["data"] = {}
                    detail["data"]["spu_info"] = spu_info
                    detail["data"]["sku_info"] = sku_list
                    detail["site_name"] = self.name
                    detail["operate"] = meta.get("operate")
                    yield detail
            else:
                self.logger.error("sku API请求错误: %s %s" % (data, response.request.body))

    @staticmethod
    def gen_category_temp(**kwargs):
        return {"name": kwargs.get("category_name", ""),
                "source_id": kwargs.get("category_id", ""),
                "source_pid": kwargs.get("parent_category_id", "") if kwargs.get("level", "") != 1 else None,
                "level": kwargs.get("level", ""),
                }

    @staticmethod
    def gen_common_params():
        """
        所有请求的params
        :return:
        """
        return urlencode((
            ('p', 'wxapp'),
            ('v', '4.6.4'),
            ('tk', 'RldCTThqY0JWVUZWdDZ4YzVEUlBHUDJIZ0h1a2JGMlVzRnNrZEVaTTJNaz0='),
            ('sh', '624'),
            ('sw', '414'),
            ('mt', 'iPhone 7 Plus<iPhone9,2>'),
        ))
