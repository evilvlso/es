import pymysql
import pandas


class ExportWorker(object):
    def __init__(self):
        self.sql_db = pymysql.connect(host='rm-uf621e7hg8ciq7a09.mysql.rds.aliyuncs.com', port=3306,
                                      user='rw_shopanalysis', password='pwd#dnf0346%kf7Aa^',
                                      database='shopping_data_analysis', charset='utf8',
                                      cursorclass=pymysql.cursors.SSCursor)

        # self.sql_db = pymysql.connect(host='10.43.1.104', port=3306,
        #                               user='root', password='BFcorp@1',
        #                               database='shopping_data_analysis', charset='utf8',
        #                               cursorclass=pymysql.cursors.SSCursor)
        self.cursor = self.sql_db.cursor()

    def export(self, site_name):
        sql = 'select * from product_sku_info inner join product_spu_info on' \
              '(product_sku_info.spu_id = product_spu_info.spu_id and product_sku_info.site_name = product_spu_info.site_name) ' \
              'where product_sku_info.site_name = "{}" and product_spu_info.status=1;'.format(site_name)

        self.cursor.execute(sql)
        items = []
        data = [k[0] for k in self.cursor.description]
        while True:
            row = self.cursor.fetchone()
            items.append(row)
            # print(row)
            if not row:
                break

        self.sql_db.close()

        print('success get {}'.format(len(items)))
        print(data)
        df = pandas.DataFrame(items)
        df.columns = data
        df.to_csv('yunji.csv', encoding='utf-8-sig')


if __name__ == '__main__':
    worker = ExportWorker()
    worker.export('yunji')
