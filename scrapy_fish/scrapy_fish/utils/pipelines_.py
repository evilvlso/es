#!/usr/bin/env python  
# -*- coding:utf-8 _*-  
""" 
@author: zhangslob 
@file: pipelines_.py 
@time: 2019/04/24
@desc: 
    
"""
import datetime
import time

from ..utils.tools.date_ import get_date,get_second
from .settings_ import *
from .items_ import HtmlItem
from scrapy.utils.python import to_unicode
from scrapy.utils.datatypes import CaselessDict
from scrapy.utils.reqser import request_to_dict


def to_unicode_dict(d):
    """ Return headers as a CaselessDict with unicode keys
    and unicode values. Multiple values are joined with ','.
    """
    return CaselessDict(
        (to_unicode(key, encoding='utf-8'),
         to_unicode(b','.join(value), encoding='utf-8'))
        for key, value in d.items())


class SaveHtmlPipeline(object):
    def __init__(self):
        self.client = mongo_client()
        self.db = ''

    def process_item(self, item, spider):
        db_name = spider.settings.get('SAVE_HTML_DB', spider.name)
        self.db = self.client.get_database()['history_{}_{}'.format(db_name, get_date())]
        data = self.save_html_(item['response'], spider)
        self.db.insert_one(dict(data))
        return item

    def save_html_(self, response, spider):
        item = HtmlItem()
        item['html'] = response.text
        item['url'] = response.url
        item['save_time'] = int(1000000*time.time())
        c = response.request.callback
        item['callback_'] = c.__func__.__name__ if c else 'parse'

        response.meta.update({'save_time': item['save_time']})

        req = request_to_dict(response.request, spider=spider)

        # 由于返回的headers的key为比特，无法直接储存需要转换
        headers = req['headers'].copy()
        req['headers'] = to_unicode_dict(headers)
        item['request'] = req

        return item


class DropItemLogPipeline(object):

    def process_item(self, item, spider):
        pass


class AddTime(object):
    def process_item(self, item: dict, spider):
        """
        增加爬虫抓取时间
        :param item:
        :param spider:
        :return:
        """
        _ = spider
        _ = self
        i = dict()
        i['crawl_time'] = datetime.datetime.utcnow()
        item.update(i)
        return item


class MySQLPipeline(object):
    """
    保存数据到MySQL
    """
    def __init__(self):
        self.db = mysql_client()
        self.cursor = self.db.cursor()

    def handle_category(self, data, spider):
        """
        处理分类信息
        :param data:
        :param spider:
        :return:
        """
        sql = "SELECT id FROM category_info WHERE source_id='{}' AND site_name='{}'"
        categories_info = data['data']
        for category_info in categories_info:
            self.cursor.execute(sql.format(category_info['source_id'], data['site_name']))
            category = self.cursor.fetchone()
            if category:
                update_sql = """
                UPDATE category_info SET {},update_time="{}" WHERE id={}""".format(
                    ', '.join(['{}="{}"'.format(i, j) for i, j in category_info.items()]),get_second(),
                    category['id']
                )
                self.execute_sql(update_sql, spider)

            else:
                insert_sql = """
                INSERT INTO category_info ({}, site_name) VALUES  ({}, '{}') """.format(
                    ', '.join(list(category_info.keys())),
                    list(category_info.values()), data['site_name']
                ).replace('[', '').replace(']', '')
                self.execute_sql(insert_sql, spider)

    def process_item(self, item, spider):
        """
        首先，查询信息是否存在，不存在插入，存在则更新
        更新的依据是主键ID
        :param item:
        :param spider:
        :return:
        """
        data = dict(item)
        if data['operate'] == 'get_categories':
            self.handle_category(data, spider)
            return item

        spu_info = data['data']['spu_info']
        sku_info = data['data']['sku_info']

        # 查询spu是否存在
        search_spu_sql = "SELECT * FROM product_spu_info WHERE site_name='{}' AND spu_id='{}'"
        self.cursor.execute(search_spu_sql.format(spu_info['site_name'], spu_info['spu_id']))
        search_spu = self.cursor.fetchone()

        if search_spu:
            # 如果存在，根据主键更新信息
            self.update_spu(spu_info, search_spu['id'], spider)
        else:
            # 如果不存在，先插入信息，再查询记录，拿到主键ID
            self.insert_into_spu(spu_info, spider)
            self.cursor.execute(search_spu_sql.format(spu_info['site_name'], spu_info['spu_id']))
            search_spu = self.cursor.fetchone()

        # 拿到spu的自增ID
        product_spu_info_id = search_spu['id']

        for sku in sku_info:
            # 查询sku是否存在
            search_spu_sql = "SELECT * FROM product_sku_info WHERE site_name='{}' AND sku_id='{}'"
            self.cursor.execute(search_spu_sql.format(sku['site_name'], sku['sku_id']))
            search_sku = self.cursor.fetchone()
            if search_sku:
                self.update_sku(sku, search_sku['id'], spider)
            else:
                self.insert_into_sku(sku, product_spu_info_id, spider)
                self.cursor.execute(search_spu_sql.format(sku['site_name'], sku['sku_id']))
                search_sku = self.cursor.fetchone()

            # 拿到sku的自增ID
            product_sku_info_id = search_sku['id']

            # 把sku数据插入历史表中
            sku.pop("crawl_time")
            self.insert_into_history(sku, product_sku_info_id, product_spu_info_id, spider)
        return item

    def insert_into_spu(self, spu_info, spider):
        spu_info['crawl_time'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        sql = """
        INSERT INTO product_spu_info
        ({})
        VALUES  ({}) """.format(
            ', '.join(list(spu_info.keys())),
            list(spu_info.values())
        ).replace('[', '').replace(']', '')
        self.execute_sql(sql, spider)

    def update_spu(self, spu_info, main_id, spider):
        """
        通过id主键去更新spu
        :param spider:
        :param main_id: id主键
        :param spu_info:
        :return:
        """
        spu_info['crawl_time'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

        sql = """
        UPDATE product_spu_info SET {},update_time="{}" WHERE id={}
        """.format(
            ', '.join(['{}="{}"'.format(i, j) for i, j in spu_info.items()]),get_second(), main_id
        )
        self.execute_sql(sql, spider)

    def update_sku(self, sku, main_id, spider):
        """
        通过id主键去更新sku
        :param spider:
        :param sku:
        :param main_id:
        :return:
        """
        sku['crawl_time'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        sql = """
                UPDATE product_sku_info SET {},update_time="{}" WHERE id={}
                """.format(
            ', '.join(["{}='{}'".format(i, j) for i, j in sku.items()]),get_second(), main_id
        )

        self.execute_sql(sql, spider)

    def insert_into_sku(self, sku, search_spu_id, spider):
        """
        插入新sku
        :param spider:
        :param sku:
        :param search_spu_id: spu主键
        :return:
        """
        sku['crawl_time'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        sql = """
        INSERT INTO product_sku_info
        ({}, product_spu_info_id)
        VALUES  ({}, {}) """.format(
            ', '.join(list(sku.keys())),
            list(sku.values()), search_spu_id
        ).replace('[', '').replace(']', '')
        self.execute_sql(sql, spider)

    def insert_into_history(self, sku, product_sku_info_id, product_spu_info_id, spider):
        """
        插入sku到历史记录表里
        需要先判断插入的表格是哪个，取模
        :param sku:
        :param product_sku_info_id: sku的自增ID
        :param product_spu_info_id: su的自增ID
        :return:
        """
        table = self.get_history_table(product_spu_info_id)

        sql = """
        INSERT INTO {}
        ({}, product_sku_info_id, product_spu_info_id)
        VALUES  ({}, {}, {}) """.format(
            table,
            ', '.join(list(sku.keys())),
            list(sku.values()), product_sku_info_id, product_spu_info_id
        ).replace('[', '').replace(']', '')

        self.execute_sql(sql, spider)

    @staticmethod
    def get_history_table(spu_id):
        """
        选择保存sku的表格
        :param spu_id: spu的主键ID
        :return:
        """
        num = divmod(int(spu_id), 32)[1]
        return 'product_sku_info_history_{}'.format(num)

    def execute_sql(self, sql, spider):
        """
        执行插入、更新操作
        :param spider:
        :param sql:
        :return:
        """
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            spider.logger.error('Exception {}, sql {}'.format(e, sql))
            self.db.rollback()


class MysqlESPipeline(object):
    """
    把数据保存到MySQL，目的是适应es，方便数据导入
    """

    def __init__(self):
        self.db = mysql_client()
        self.cursor = self.db.cursor()

    def process_item(self, item, spider):
        data = dict(item)
        if data['operate'] == 'get_categories':
            return item

        spu_info = data['data']['spu_info']
        for sku in data['data']['sku_info']:
            es_data = self.extract_info(sku, spu_info)

            # 查询数据是否存在，不存在则插入，存在则更新
            judge_sql = "SELECT * FROM es_sku_info WHERE site_name='{}' AND sku_id='{}'"
            self.cursor.execute(judge_sql.format(es_data['site_name'], es_data['sku_id']))
            judge_result = self.cursor.fetchone()

            if judge_result:
                sql = """UPDATE es_sku_info SET {} WHERE id={} """.format(
                    ', '.join(["{}='{}'".format(i, j) for i, j in sku.items()]), judge_result['id']
                )

            else:
                sql = """INSERT INTO es_sku_info ({}) VALUES  ({}) """.format(
                    ', '.join(list(es_data.keys())), list(es_data.values())
                ).replace('[', '').replace(']', '')
            self.execute_sql(sql, spider)
        return item

    @staticmethod
    def extract_info(sku, spu_info):
        """
        如果抓取的数据不含有某字段，请自行注释
        :param sku:
        :param spu_info:
        :return:
        """
        es_data = dict()
        es_data['sku_id'] = sku['sku_id']
        es_data['spu_id'] = sku['spu_id']
        es_data['site_name'] = sku['site_name']
        es_data['title'] = spu_info['title']
        # es_data['brand'] = spu_info['brand']
        es_data['category_one'] = spu_info['category_one']
        es_data['category_two'] = spu_info['category_two']
        # es_data['category_three'] = spu_info['category_three']
        es_data['category_code'] = spu_info['category_code']
        # es_data['sold_count'] = spu_info['sold_count']
        es_data['feature'] = spu_info['feature']
        es_data['spec'] = sku['spec']
        es_data['origin_price'] = sku['origin_price']
        es_data['discount_price'] = sku['discount_price']
        # es_data['coupon_price'] = sku['coupon_price']
        # es_data['market_price'] = sku['market_price']
        # es_data['pay_off'] = sku['pay_off']
        es_data['status'] = 1  # 1上架
        es_data['crawl_time'] = datetime.datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        return es_data

    def execute_sql(self, sql, spider):
        """
        执行插入、更新操作
        :param spider:
        :param sql:
        :return:
        """
        try:
            self.cursor.execute(sql)
            self.db.commit()
        except Exception as e:
            spider.logger.error('Exception {}, sql {}'.format(e, sql))
            self.db.rollback()
