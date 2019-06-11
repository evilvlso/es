# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class CategoryItem(scrapy.Item):

    _id = scrapy.Field()
    data = scrapy.Field()
    operate = scrapy.Field()
    site_name = scrapy.Field()
    crawl_time = scrapy.Field()
    mongo_id = scrapy.Field()


class DetailItem(scrapy.Item):
    _id = scrapy.Field()
    data = scrapy.Field()
    operate = scrapy.Field()
    site_name = scrapy.Field()
    category1_name = scrapy.Field()
    category2_name = scrapy.Field()
    category3_name = scrapy.Field()
    crawl_time = scrapy.Field()
    mongo_id = scrapy.Field()
