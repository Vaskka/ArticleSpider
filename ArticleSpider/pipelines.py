# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.pipelines.images import ImagesPipeline
from twisted.enterprise import adbapi
import MySQLdb
import MySQLdb.cursors
from scrapy.exporters import JsonItemExporter


class ArticlespiderPipeline(object):
    def process_item(self, item, spider):
        return item


"""
class ArticleJsonPipeline(object):
    # 未使用框架保存数据到json
    def __init__(self):
        self.file = codecs.open('article.json', 'w', encoding='utf-8')

    def process_item(self, item, spider):
        line = json.dumps(dict(item._values), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

    def spider_closed(self, spider):
        self.file.close()
"""


class ArticleJsonExplorerPipeline(object):
    # 使用框架保存数据到json
    def __init__(self):
        self.file = open('article_explorer', 'wb')
        self.json_explorer = JsonItemExporter(self.file, encoding='utf-8', ensure_ascii=False)
        self.json_explorer.start_exporting()

    def process_item(self, item, spider):
        self.json_explorer.export_item(item)
        return item

    def spider_closed(self, spider):
        self.json_explorer.finish_exporting()
        self.file.close()


class MysqlTwistedPipeline(object):
    #使用Twisted异步保存数据到mysql
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings['MYSQL_HOST'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            db=settings['MYSQL_DBNAME'],
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
            use_unicode=True
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparams)
        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将item处理变成异步操作
        query = self.dbpool.runInteraction(self.do_insert, item)
        query.addErrback(self.handle_error)


    def handle_error(self, failure):
        print(failure)


    def do_insert(self, cursor, item):
        #具体插入操作
        SQL_insert = """
            insert into jobbolearticle(url_object_id, url, title, tag, create_date, source_href, source_name, main_text, vote, comment_num, img_url, img_path)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(SQL_insert, (item['url_object_id'],
                                    item['url'],
                                    item['title'],
                                    item['tag'],
                                    item['date'],
                                    item['source_href'],
                                    item['source_name'],
                                    item['main_text'],
                                    item['vote'],
                                    item.get('comment_num', '0'),
                                    item['img_url'],
                                    item['img_path']))


class ArticleImgPipeline(ImagesPipeline):
    def item_completed(self, results, item, info):
        img_file_path = ""
        for (ok, value) in results:
            img_file_path = value['path']
        item['img_path'] = img_file_path

        return item
