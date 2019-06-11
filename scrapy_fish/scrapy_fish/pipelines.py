# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from .utils.settings_ import *
import json

queue_name = "scrawl_finished_notify_queue_common"


class MongoDbPipeline(object):

    def __init__(self):
        self.db = mongo_client().get_database()

    def process_item(self, item, spider):
        collection = self.db[item['site_name']]
        data = collection.find_one({"_id": item["_id"]})
        if data is None:
            mongo_id = collection.insert(item)
        else:
            collection.update({"_id": data["_id"]}, item)
            mongo_id = data["_id"]
        item["mongo_id"] = str(mongo_id)
        return item


class NotifyPipeline(object):

    def process_item(self, item, spider):
        """
        发送消息给MQ，通知JAVA程序来处理mongo中的数据
        :param item:
        :param spider:
        :return:
        """
        notify_dict = {"mongo_id": item["mongo_id"], "site_name": item['site_name'], "operate": item['operate']}
        notify_json = json.dumps(notify_dict, default=lambda x: x.__dict__)

        connection = pika_client()
        channel = connection.channel()
        channel.queue_declare(queue=queue_name, durable=True)
        channel.basic_publish(exchange='', routing_key=queue_name, body=notify_json,
                              properties=pika.BasicProperties(delivery_mode=1))
        spider.logger.debug("数据抓取完成，发送回调给调用方, body=" + notify_json)
        connection.close()
        return item
