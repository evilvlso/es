import pika
import json

from settings_ import *

spider_name = 'example'

credentials = pika.PlainCredentials(RABBIT_USERNAME, RABBIT_PASSWORD)
parameters = pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT, virtual_host=RABBIT_VHOST,
                                       credentials=credentials)
client = pika.BlockingConnection(parameters)
channel = client.channel()

data = {"operate": "get_categories", "site_name": spider_name}

# data = {"meta": {"sku_id": "10915", "spu_id": "2859", 'category_id': "141", "category_name" : "水产"},
#         "operate": "get_product_by_sku", "site_name": spider_name}
#
# data = {"meta": {"category_id": "fd378c09641d1adf", "category_name": "厨房工具", 'parent_category_id': '8182'},
#         "operate": "get_product_by_category", "site_name": spider_name}


def send(data):
    channel.queue_declare(queue='spider_request_queue_{}'.format(spider_name), durable=True, )
    channel.basic_publish(exchange='',
                          routing_key='spider_request_queue_{}'.format(spider_name),
                          body=json.dumps(data))
    print(" [x] Sent {}".format(data))


if __name__ == '__main__':
    send(data)

