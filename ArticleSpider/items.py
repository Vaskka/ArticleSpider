# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose, TakeFirst, Join

from ArticleSpider.util import common

import re


class ArticlespiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


def to_md5url(value):
    """将urlMD5"""
    value = common.get_md5(value)
    return value


def to_puredate(value):
    """去掉日期多余的字符"""
    value = value.strip().replace("·", "").strip()
    return value


def to_aslist(value):
    return value


def to_getcommentnum(value):
    value = value.replace(" ", "")
    result = re.match("^([0-9]+).[评论]$", value)
    if result:
        return result.group(1)
    else:
        return value


def to_kickstr(value):
    if "评论" in value:
        return ""
    else:
        return value


class ArticleItemLoader(ItemLoader):
    """自定义ItemLoader的output_processor方式"""
    default_output_processor = TakeFirst()


class JobboleItem(scrapy.Item):
    # 定制article的item
    url = scrapy.Field()
    url_object_id = scrapy.Field(
        input_processor=MapCompose(to_md5url)
    )
    title = scrapy.Field()
    date = scrapy.Field(
        input_processor=MapCompose(to_puredate)
    )
    tag = scrapy.Field(
        input_processor=MapCompose(to_kickstr),
        output_processor=Join(",")
    )
    source_href = scrapy.Field()
    source_name = scrapy.Field()
    main_text = scrapy.Field()
    vote = scrapy.Field()
    img_url = scrapy.Field(
        output_processor=MapCompose(to_aslist)
    )
    img_path = scrapy.Field()
    comment_num = scrapy.Field(
        input_processor=MapCompose(to_getcommentnum)
    )



