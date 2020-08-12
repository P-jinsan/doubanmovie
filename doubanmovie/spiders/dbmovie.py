# -*- coding: utf-8 -*-
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
