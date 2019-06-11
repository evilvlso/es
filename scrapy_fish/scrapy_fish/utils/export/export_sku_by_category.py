#!/usr/bin/env python  
# -*- coding:utf-8 -*-
""" 
@author: zhangslob 
@file: export_all_site.py 
@time: 2019/04/28
@desc: 
    导出全量的某品牌数据
    因为数据量达到百万级别，一次性是没办法全部取出的。所以要分页。
    先计算总数，每次取1000条，取出来之后直接保存到csv文件

    最后需要添加一行，也就是csv的列名
"""

import pymysql
import csv


class ExportWorker(object):
    def __init__(self, site_name, category):
        self.site_name = site_name
        self.category = category
        self.sql_db = pymysql.connect(host='rm-uf621e7hg8ciq7a09.mysql.rds.aliyuncs.com', port=3306,
                                      user='rw_shopanalysis', password='pwd#dnf0346%kf7Aa^',
                                      database='shopping_data_analysis', charset='utf8',
                                      cursorclass=pymysql.cursors.DictCursor)

        # self.sql_db = pymysql.connect(host='10.43.1.104', port=3306,
        #                               user='root', password='BFcorp@1',
        #                               database='shopping_data_analysis', charset='utf8',
        #                               cursorclass=pymysql.cursors.SSCursor)
        self.cursor = self.sql_db.cursor()

    def export(self):
        sql = "select * from product_sku_info inner join product_spu_info on" \
              " (product_sku_info.spu_id = product_spu_info.spu_id and " \
              "product_sku_info.site_name = product_spu_info.site_name and" \
              " product_spu_info.category_one='{}') where product_sku_info.site_name = '{}'".format(
            self.category, self.site_name
        )

        self.cursor.execute(sql)
        r = self.cursor.fetchall()
        self.write_to_csv(r)
        self.sql_db.close()

    def write_to_csv(self, items):
        with open('{}_{}.csv'.format(self.site_name, self.category), 'a+', newline='', encoding='utf_8_sig') as f:
            writer = csv.writer(f)
            i = 0
            for item in items:
                i += 1
                if i == 1:
                    row = list(item.keys())
                else:
                    row = list(item.values())
                writer.writerow(row)
                print('success write {}'.format(i))


if __name__ == '__main__':
    for i in ['个人洗护', '美容彩妆', '全球工厂店']:
        worker = ExportWorker('kaola', i)
        worker.export()
