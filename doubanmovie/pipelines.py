# -*- coding: utf-8 -*-
import pymysql
from twisted.enterprise import adbapi
import copy
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

class DoubanmoviePipeline(object):
    def __init__(self,dbpool):
        self.dbpool=dbpool

    @classmethod
    def from_settings(cls,settings):
        """
                数据库建立连接
                :param settings: 配置参数
                :return: 实例化参数
                """
        adbparams = dict(
            host=settings['MYSQL_HOST'],  # 读取settings中的配置
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            passwd=settings['MYSQL_PASSWD'],
            charset='utf8',#不要"-"
            cursorclass=pymysql.cursors.DictCursor,
        )
        dbpool = adbapi.ConnectionPool('pymysql', **adbparams)  # **表示将字典扩展为关键字参数,相当于host=xxx,db=yyy....
        return cls(dbpool)  # 相当于dbpool付给了这个类，self中可以得到

        # pipeline默认调用
    def process_item(self, item, spider):
        asynItem = copy.deepcopy(item) #深度拷贝 为解决爬取与插入速度不统一导致的数据重复0
        query = self.dbpool.runInteraction(self._conditional_insert, asynItem)  # 调用插入的方法
        query.addCallback(self.handle_error)  # 调用异常处理方法

        # 写入数据库中
    def _conditional_insert(self, course, item):
            # print item['name']
            #sql = "insert into doubanmovie(name,url) values(%s,%s)"
            sql = """insert into doubanmovie(num,title,rating,quote) value (%s, %s, %s, %s)"""
            # params = (item["name"], item["url"])
            course.execute(sql, (int(item['num']),item['title'],item['star'],pymysql.escape_string(item['quote'])))
    def handle_error(self, failure):
            if failure:
                # 打印错误信息
                print(failure)
#小数据
    # def __init__(self):
#     #     # 连接数据库
#     #     self.conn = pymysql.connect('localhost','root','123456','douban',charset='utf8')
#     #     # 通过cursor执行增删查改
#     #     self.cursor = self.conn.cursor()
#     # def process_item(self, item, spider):
#     #     # 插入数据
#     #     insert_sql ="""insert into doubanmovie(num,title,rating,quote) value (%s, %s, %s, %s)"""
#     #     self.cursor.execute(insert_sql,(item['num'],item['title'],item['star'],item['quote']))
#     #     # 提交sql语句
#     #     self.conn.commit()
#     # def close_spider(self,spider):
#     #     #关闭游标和连接
#     #     self.cursor.close()
#     #     self.conn.close()