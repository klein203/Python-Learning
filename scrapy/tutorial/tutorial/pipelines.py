# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import psycopg2

class TutorialPipeline(object):
    def process_item(self, item, spider):
        return item


class CxcarPipeline(object):
    def __init__(self):
        self.connection = psycopg2.connect("dbname='scrapy_db' user='scrapy_user' password='scrapy'")
        self.connection.autocommit = True
    
    def open_spider(self, spider):
        self.cursor = self.connection.cursor()
        self.prepare_insert_sql = 'prepare prepare_insert(varchar, varchar, varchar, numeric) as insert into t_cxcar (series_name, model_name, price, price_num, create_timestamp, update_timestamp) values ($1, $2, $3, $4, now(), now())'
        self.cursor.execute(self.prepare_insert_sql)
        
    def close_spider(self, spider):
        self.cursor.close()
        self.connection.close()
    
    def process_item(self, item, spider):
        self.cursor.execute('execute prepare_insert(%s, %s, %s, %s)', (item['series_name'], item['model_name'], item['price'], item['price_num']))
        return item
