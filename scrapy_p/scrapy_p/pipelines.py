# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
import codecs
import json
import MySQLdb
import MySQLdb.cursors
from twisted.enterprise import adbapi

#可以拦截item 保存到数据库
class ScrapyPPipeline(object):
    def process_item(self, item, spider):
        return item

class JsonWithEncodingPipeline(object):
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding = 'utf-8')

    #process item must return the item
    def process_item(self, item, spider):
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_close(self, spider):
        self.file.close()

class JsonExporterPipeline(object):
    def __init__(self):
        #调用scrapy提供的json exporter导出json文件
        self.file = open('article_expoter.json', 'wb')
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item


class ArticleImagePipeline(ImagesPipeline):

    def item_completed(self, results, item, info):
        """
        result : type tuple
                (boolean, dict{'checksum:img_name,
                                'path': local directory,
                                'url': download url,'})
        """
        if "front_image_url" in item:
            for ok, value in results:
                img_file_path = value['path']
                item["front_img_path"] = img_file_path

        return item

class MysqlPipeline(object):
    #同步机制写入mysql
    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', '1997XXxx', 'article_spider', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """insert into jobbole_article(title, create_date, url ,url_object_id, fav_num) 
            VALUES (%s, %s, %s, %s, %s)"""
        self.cursor.execute(insert_sql, (item["title"], item["create_date"], item["url"], item["url_object_id"],  item["fav_num"]))
        self.conn.commit()

#异步操作，将爬取的数据存入数据库, 支持关系型数据库
class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls,settings):
        #参数名称必须与mysql.connections 一致
        dbparm = dict(
            host = settings['MYSQL_HOST'],
            db = settings['MYSQL_DBNAME'],
            password = settings["MYSQL_PWD"],
            user = settings['MYSQL_USER'],
            charset = 'utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True,

        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparm)
        return cls(dbpool)

    def process_item(self, item, spider):
        #使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error, item, spider) #处理异常

    def handle_error(self, failure, item, spider):
        #自定义处理异步插入的异常
        print (failure)

    def do_insert(self, cursor, item):
        #执行具体的插入
        #根据不同的item 构建不同的sql语句并插入到mysql中
        # insert_sql, params = item.get_insert_sql()
        # cursor.execute(insert_sql, params)
        insert_sql = """insert into jobbole_article(title, create_date, url ,url_object_id, fav_num) 
            VALUES (%s, %s, %s, %s, %s)"""
        cursor.execute(insert_sql, (item["title"], item["create_date"], item["url"], item["url_object_id"],  item["fav_num"]))
