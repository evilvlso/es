import pika
import redis
import json
from .settings_ import *


class MQManager(object):

    def __init__(self, spider_name, logger):
        self.logger = logger
        self.spider_name = spider_name
        self.queue_name = 'spider_request_queue_{}'.format(spider_name)

        host = RABBIT_HOST
        port = RABBIT_PORT
        username = RABBIT_USERNAME
        password = RABBIT_PASSWORD
        virtual_host = RABBIT_VHOST
        credentials = pika.PlainCredentials(username, password)
        parameters = pika.ConnectionParameters(host=host, port=port, virtual_host=virtual_host,
                                               credentials=credentials)
        self.client = pika.BlockingConnection(parameters)
        self.channel = self.client.channel()
        self.redis_client = redis.Redis.from_url(REDIS_URL)

    def callback(self, ch, method, propertites, body):
        self.logger.info(" [x] 收到爬虫请求 %r" % (body,))
        req_info = json.loads(body)
        site_name = req_info['site_name']
        if site_name == self.spider_name:
            self.redis_client.sadd('{}:start_urls'.format(self.spider_name), body)
        else:
            self.send(self.queue_name, body)

    def receive(self, queue):
        self.channel.queue_declare(queue=queue, durable=True)
        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(self.callback, queue, no_ack=True)
        self.logger.info(' [*] Waiting for messages. To exit press CTRL+C')
        self.channel.start_consuming()

    def send(self, queue, body):
        self.channel.queue_declare(queue=queue, durable=True)
        self.channel.basic_publish(exchange='', routing_key=queue, body=body,
                                   properties=pika.BasicProperties(delivery_mode=2))

    def __exit__(self):
        self.client.close()


def mq_main(spider_name, logger):
    manager = MQManager(spider_name, logger)
    manager.receive('spider_request_queue_{}'.format(spider_name))
