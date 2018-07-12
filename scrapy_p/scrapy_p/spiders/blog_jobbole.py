# -*- coding: utf-8 -*-
import scrapy
import re
from scrapy_p.utils.common import get_md5
from scrapy.http import Request
from urllib import parse
from scrapy_p.items import JobBoleArticleItem
from scrapy_p.items import ArticleItemLoader

class BlogJobboleSpider(scrapy.Spider):
    name = 'blog_jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse_detail(self, response):
        article_item = JobBoleArticleItem()
        # front_img_url = response.meta.get("front_img", "") #文章封面图
        # title = response.xpath('//div[@class = "entry-header"]/h1/text()').extract_first("")
        # create_date = response.xpath('//p[@class = "entry-meta-hide-on-mobile"]\
        #     /text()').extract()[0].strip().replace("·", "").strip()
        # thumbs_up = response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()').extract()[0]
        # if thumbs_up:
        #     thumbs_up = int(thumbs_up)
        # else:
        #     thumbs_up = 0
        # fav_num = response.xpath('//span[contains(@class, "bookmark-btn")]/text()')\
        #                      .extract()[0]
        # match_re =  re.match(".*?(\d+).*", fav_num)
        # if match_re:
        #     fav_num = int(match_re.group(1))
        # else:
        #     fav_num = 0
        # comment = response.xpath('//a[@href = "#article-comment"]/span/text()').extract()[0]
        # match_re2 =  re.match(".*?(\d+).*", comment)
        #
        # if match_re2:
        #     comment = int(match_re2.group(1))
        # else:
        #     comment = 0
        # #获取正文内容: 粗暴做法， 正文标签全部保存
        #
        # content = response.xpath("//div[@class = 'entry']").extract()
        # tag_list = response.xpath('//p[@class ="entry-meta-hide-on-mobile"]/a/text()').extract()
        # tag_list = [ i for i in tag_list if not i.strip().endswith("评论")]
        # tags = ','.join(tag_list)
        #
        # article_item["title"] = codecs.decode((title.encode('utf-8')),'utf-8')
        # try:
        #     create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
        # except Exception as e:
        #     create_date = datetime.datetime.now().date()

        # article_item["create_date"]= create_date
        # article_item["url"] = response.url
        # article_item["url_object_id"] = get_md5(response.url)
        # article_item["front_img_url"] = [front_img_url]
        # article_item["thumbs_up"]= thumbs_up
        # article_item["fav_num"] = fav_num
        # article_item["comment"] = comment
        # article_item["tags"] = tags
        # article_item["content"] = content

        #通过ItemLoader 加载item
        item_loader = ArticleItemLoader(item = JobBoleArticleItem(), response = response)
        front_img_url = response.meta.get("front_img_url", "")  # 文章封面图
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_value("front_img_url", [front_img_url])
        item_loader.add_css("thumbs_up", ".vote-post-up h10::text")
        item_loader.add_css("comment", "a[href='#article-comment'] span::text")
        item_loader.add_css("fav_num", ".bookmark-btn::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")

        article_item = item_loader.load_item()

        yield article_item



    def parse(self, response):
        """
        1. 获取文章列表中的url并交给解析函数进行具体字段解析
        2. 获取下一页的url并交给scrapy进行下载， 下载完成后交给parse
        :param response:
        :return:
        """
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            #parse 完整url
            img_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url = parse.urljoin(response.url, post_url),meta = {"front_img": img_url}, callback = self.parse_detail)

            #提取下一页url
            next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
            if next_url:
                yield Request(url = parse.urljoin(response.url, next_url), callback = self.parse)



