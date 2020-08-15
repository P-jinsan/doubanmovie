## 环境
Pycharm、Python3.8、谷歌浏览器
 ## 要求
 1. 网址：[https://movie.douban.com/top250/](https://movie.douban.com/top250/)
 2. 信息要求：序号、标题、评分、评语
 3. 将获取的信息保存到数据库中
 ## 注意
 获取的信息可能不只是一页
 ## 过程(只列出需要修改的文件)
 1.dbmovie.py
 
与练习一类似，只是要注意存在数据缺失的问题(评语可能没有)
```python
import scrapy
import re
from doubanmovie.items import DoubanmovieItem
from urllib import parse
class DbmovieSpider(scrapy.Spider):
    name = 'dbmovie'
    #allowed_domains = ['https://movie.douban.com/top250']
    start_urls = ['https://movie.douban.com/top250/',]
    def parse(self, response):
        item = DoubanmovieItem()
        selector = scrapy.Selector(response)
        movies = selector.xpath('//div[@class="item"]')
        for each in movies:
            num = each.xpath('div[@class="pic"]/em/text()').extract()[0]
            title = each.xpath('div[@class="info"]/div[@class="hd"]/a/span[@class="title"]/text()').extract()[0]
            star = each.xpath('div[@class="info"]/div[@class="bd"]/div[@class="star"]/span[@class="rating_num"]/text()').extract()[0]
            # star = re.search('<span class="rating_num" property="v:average">(.*?)</span>', each.extract(), re.S).group(1)
            quote = each.xpath('div[@class="info"]/div[@class="bd"]/p[@class="quote"]/span[@class="inq"]/text()').extract_first()
            if quote is None:
                quote = ' '
            item['quote'] = quote
            item['star'] = star
            item['title'] = title
            item['num'] = num
            yield item
            nextPage = selector.xpath('//span[@class="next"]/link/@href').extract_first()
            if nextPage:
                next = response.urljoin(nextPage)
                print(next)
                yield scrapy.http.Request(next,callback=self.parse)
```

2. item.py

```python
import scrapy
class DoubanmovieItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    title = scrapy.Field()
    quote = scrapy.Field()
    star = scrapy.Field()
    num = scrapy.Field()
```

3.  settings.py

```python
BOT_NAME = 'doubanmovie'
SPIDER_MODULES = ['doubanmovie.spiders']
NEWSPIDER_MODULE = 'doubanmovie.spiders'
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.3; WOW64; rv:45.0) Gecko/20100101 Firefox/45.0'
ROBOTSTXT_OBEY = True
#保存在数据库
MYSQL_HOST = 'localhost'
MYSQL_DBNAME = 'douban'
MYSQL_USER = 'root'
MYSQL_PASSWD = '123456'
MYSQL_PORT = 3306
ITEM_PIPELINES = {
   'doubanmovie.pipelines.DoubanmoviePipeline': 300,
}
```

4. pipelines.py
```python
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
```

5. main.py

```python
from scrapy import cmdline
cmdline.execute("scrapy crawl dbmovie".split())
```
## 结束
爬取大量数据可能会出现爬取速度与插入速度不匹配产生大量重复数据，因此需要进行深度拷贝

```python
asynItem = copy.deepcopy(item) #深度拷贝 为解决爬取与插入速度不统一导致的数据重复0
```
