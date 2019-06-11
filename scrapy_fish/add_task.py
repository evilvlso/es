#!/usr/bin/env python  
# -*- coding:utf-8 -*-  
""" 
@author: zhangslob 
@file: add_task.py 
@time: 2019/05/20
@desc: 
    python3 -m add_task.py add_category

    0 13 * * *  source /etc/profile && cd scrapy_fish && /usr/bin/python3 -m scrapy_fish.add_task add_category
    >/home/jenkins/scrapy_fish/scrapy_fish/add_task.log 2>&1

"""
import os
import sys
import json
import redis
import pymongo
import pymysql
import logging
import logging.handlers


def get_logger(name, level=logging.DEBUG, file=True, log_dir=''):
    _logger = logging.getLogger(name)
    _logger.setLevel(level)
    formats = logging.Formatter(
        '%(asctime)s - %(name)s - %(lineno)d - %(levelname)s - %(threadName)s - %(message)s')

    if file:
        if not log_dir:
            log_dir = os.path.abspath(
                os.path.dirname(__file__) + os.path.sep + "./" + 'logs')
        log_dir = os.path.expanduser(log_dir)
        if not os.path.exists(log_dir) or not os.path.isdir(log_dir):
            os.makedirs(log_dir, exist_ok=True)

        file_handler = logging.handlers.TimedRotatingFileHandler(
            filename=os.path.join(log_dir, '{}.log'.format(name.replace('.py', ''))), when='D', encoding='utf-8'
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formats)
        _logger.addHandler(file_handler)

    stream_headler = logging.StreamHandler()
    stream_headler.setLevel(level)
    stream_headler.setFormatter(formats)
    _logger.addHandler(stream_headler)

    return _logger


ENV = os.environ.get('SPIDER_ENV', None)
# ENV = 'release' if platform.system() == 'Linux' else 'test'
print('env {}'.format(ENV))

if ENV != 'release':
    REDIS_URL = 'redis://:@10.32.16.101:6379/1'

    # MongoDB
    MONGODB_URL = 'mongodb://10.43.1.104:27017/shopping_spider'

    # Rabbit
    RABBIT_HOST = '10.43.1.103'
    RABBIT_PORT = 5672
    RABBIT_USERNAME = 'admin'
    RABBIT_PASSWORD = '123456abc'
    RABBIT_VHOST = 'shopping_data_analysis_test'

    MYSQL_HOST = '10.43.1.104'
    MYSQL_PORT = 3306
    MYSQL_USER = 'root'
    MYSQL_PASSWORD = 'BFcorp@1'
    MYSQL_DB = 'shopping_data_analysis'
    MYSQL_CHARSET = 'utf8'

else:
    REDIS_URL = 'redis://:toW3cBee@supplychain-master.redis.blackfi.sh:6379/1'

    # MongoDB
    MONGODB_URL = 'mongodb://rw_shopspider:vcB1ack!#F1sHrbT@' \
                  'dds-uf6b8a202b764f841.mongodb.rds.aliyuncs.com:3717/shopping_spider'

    # Rabbit
    RABBIT_HOST = '10.6.50.93'
    RABBIT_PORT = '5672'
    RABBIT_USERNAME = 'admin'
    RABBIT_PASSWORD = 'gTHud7PQ'
    RABBIT_VHOST = '/shopping_data_analysis'

    MYSQL_HOST = 'rm-uf621e7hg8ciq7a09.mysql.rds.aliyuncs.com'
    MYSQL_PORT = 3306
    MYSQL_USER = 'rw_shopanalysis'
    MYSQL_PASSWORD = 'pwd#dnf0346%kf7Aa^'
    MYSQL_DB = 'shopping_data_analysis'
    MYSQL_CHARSET = 'utf8'


def mongo_client():
    return pymongo.MongoClient(MONGODB_URL)


def mysql_client(cursorclass=pymysql.cursors.DictCursor):
    return pymysql.connect(
        host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER, password=MYSQL_PASSWORD,
        database=MYSQL_DB, charset='utf8', cursorclass=cursorclass)


def redis_client():
    return redis.from_url(REDIS_URL)


def pika_client():
    credentials = pika.PlainCredentials(RABBIT_USERNAME, RABBIT_PASSWORD)
    parameters = pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT, virtual_host=RABBIT_VHOST,
                                           credentials=credentials)
    return pika.BlockingConnection(parameters)


logger = get_logger(name='add_task', file=False)
site_name = 'mryitao'
redis_key = '{}:start_urls'.format(site_name)
logger.info('start add task for site {}'.format(site_name))

r = redis_client()
mysql = mysql_client()


def add_category():
    r.sadd(redis_key, json.dumps({"operate": "get_categories"}))
    logger.info('finish add operate get_categories to redis')


def add_sku_id():

    sql = """
    select c.category_code,b.spu_id,c.category_one,c.category_two,c.category_three from product_mapping as a
    inner join product_sku_info as b 
    on a.competitor_sku_id=b.sku_id and a.site_name=b.site_name
    inner join product_spu_info as c
    on a.site_name=c.site_name and b.spu_id=c.spu_id
    where a.site_name="{}" group by b.spu_id
    """.format(site_name)


    cursor = mysql.cursor()
    cursor.execute(sql)
    sku_list = cursor.fetchall()
    sku_list_ = [
        json.dumps(
            {"operate": "get_product_by_sku",
             "meta":  {'category_code': i['category_code'], "spu_id": i['spu_id'],
                       "category_one": i["category_one"],
                       "category_two": i["category_two"],
                       "category_three": i["category_three"]}})
                       for i in sku_list ]
    logger.info('get sku len {}'.format(len(sku_list)))
    r.sadd(redis_key, *sku_list_)
    logger.info('finish add operate get_product_by_sku to redis')


if __name__ == '__main__':
    args = sys.argv
    if len(args) > 1:
        if 'add_category' in args[1]:
            add_category()
        else:
            add_sku_id()
    else:
        logger.info('添加任务脚本 需要命令执行。`add_category`发送抓取分类指令，`add_sku_id`发送抓取指定sku指令')
