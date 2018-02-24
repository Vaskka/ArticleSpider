# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request

from urllib import parse

from ArticleSpider.items import JobboleItem, ArticleItemLoader


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        1。获取列表中所有的url，并交给scrapy
        2。获取指向下一页的url，并交给scrapy
        """
        # 获得页面中所有的url,并交给scrapy
        post_nodes = response.css('#archive div.floated-thumb div.post-thumb a')
        for post_node in post_nodes:
            # 图片的url
            img_url = post_node.css("img::attr(src)").extract_first("")
            # 正文的url
            main_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, main_url), meta={"front_img_url": img_url}, callback=self.parse__detail)

        # 获得下一页的url，并交给scrapy
        next_url = response.css('a.next.page-numbers::attr(href)').extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse__detail(self, response):
        """
        #通过xpath提取

        #获取文章标题
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract()[0]

        #获取日期
        time_str = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/text()').extract()[0]
        time = time_str.replace("·", "").strip()

        #获取tag
        tag_list = response.xpath('//p[@class="entry-meta-hide-on-mobile"]/a/text()').extract()
        tag = ""
        for stag in tag_list:
            tag += stag
            tag += " "
        tag.rstrip()

        #获取原文出处
        source_href = response.xpath('//div[@class="copyright-area"]/a/@href').extract()[0]
        source_name = response.xpath('//div[@class="copyright-area"]/a/text()').extract()[0]

        #获取正文
        main_text_list = response.xpath('//div[@class="entry"]').extract()
        main_text = ""
        for text in main_text_list:
            main_text += text

        #获取点赞数
        vote = response.xpath('//span[contains(@class, "vote-post-up")]/h10/text()').extract()[0]

        """
        """
        # 通过css提取

        # 获取标题
        title = response.css('div.entry-header h1::text').extract_first("")

        # 获取日期
        date_str = response.css('p.entry-meta-hide-on-mobile::text').extract_first("")
        date = date_str.replace("·", "").strip()

        # 获取tag
        tag = ""
        tag_list = response.css('p.entry-meta-hide-on-mobile a::text').extract()
        for stag in tag_list:
            tag += stag
            tag += " "
        tag.rstrip()

        # 获取原文出处
        source_href = response.css('div.copyright-area a::attr(href)').extract_first("")
        source_name = response.css('div.copyright-area a::text').extract_first("")

        # 获取正文
        main_text = response.css('.entry').extract_first("")

        # 获取点赞数
        vote = response.css('span.vote-post-up h10::text').extract_first("")

        # 获取图片
        img_url = response.meta['front_img_url']

        # 实例化Item
        article_item = JobboleItem()
        article_item['url'] = response.url
        article_item['url_object_id'] = cm.get_md5(response.url)
        article_item['title'] = title

        try:
            date = datetime.datetime.strptime(date, "%Y/%M/%D").date()
        except Exception as e:
            date = datetime.datetime.now().date()

        article_item['date'] = date
        article_item['tag'] = tag
        article_item['source_href'] = source_href
        article_item['source_name'] = source_name
        article_item['main_text'] = main_text
        article_item['vote'] = vote
        article_item['img_url'] = [img_url]
        article_item['img_path'] = img_url
        """

        # 通过ItemLoader提取item
        article_item = JobboleItem()
        item_loader = ArticleItemLoader(item=article_item, response=response)
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", response.url)
        item_loader.add_css("title", "div.entry-header h1::text")
        item_loader.add_css("date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_css("tag", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("source_href", "div.copyright-area a::attr(href)")
        item_loader.add_css("source_name", "div.copyright-area a::text")
        item_loader.add_css("main_text", ".entry")
        item_loader.add_css("vote", "span.vote-post-up h10::text")
        item_loader.add_value("img_url", response.meta['front_img_url'])
        item_loader.add_value("img_path", response.meta['front_img_url'])
        item_loader.add_xpath("comment_num", '//div[@class="entry-meta"]/p/a[@href="#article-comment"]/text()')

        article_item = item_loader.load_item()

        yield article_item
        pass
