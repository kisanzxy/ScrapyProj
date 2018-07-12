# -*- coding: utf-8 -*-
import scrapy
import re

class BlogJobboleSpider(scrapy.Spider):
    name = 'blog_jobbole_copy'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/110287/']

    def parse(self, response):
        #css selector
        title =  response.css(".entry-header h1::text").extract()

        create_date = response.css(".entry-meta-hide-on-mobile::text")\
            .extract()[0].strip().replace("·", "").strip()
        thumbs_up =  response.css(".vote-post-up h10::text").extract()
        fav_num = response.css(".bookmark-btn::text").extract()[0]
        match_re =  re.match(".*?(\d+).*", fav_num)
        if match_re:
            fav_num = match_re.group(1)

        comment = response.css('#post-110287 > div.entry > div.post-adds > a span::text').extract()[0]
        match_re2 =  re.match(".*?(\d+).*", comment)
        if match_re2:
             comment = match_re2.group(1)
        #获取正文内容: 粗暴做法， 正文标签全部保存

        content = response.xpath("//div[@class = 'entry']").extract()
        tag_list = response.css('.entry-meta-hide-on-mobile a::text').extract()
        tag_list = [ i for i in tag_list if not i.strip().endswith("评论")]
        tag = ','.join(tag_list)
        pass


