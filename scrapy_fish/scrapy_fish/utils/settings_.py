#!/usr/bin/env python  
# -*- coding:utf-8 _*-  
""" 
@author: zhangslob 
@file: settings_.py
@time: 2019/04/12
@desc: 
    开发环境配置
"""  

import os
import pika
import redis
import pymongo
import pymysql

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



