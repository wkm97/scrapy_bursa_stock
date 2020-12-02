# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class HistoricalDataItem(scrapy.Item):
    data = scrapy.Field()
    bursacode = scrapy.Field()
    stockcode = scrapy.Field()
    source = scrapy.Field()

class TickerInfoItem(scrapy.Item):
    stockcode = scrapy.Field()
    bursacode = scrapy.Field()
    bloomberg = scrapy.Field()
    alias = scrapy.Field()
    name = scrapy.Field()
    reuters = scrapy.Field()
    economicsectorcode = scrapy.Field()
    industrygroupcode = scrapy.Field()
    businesssummary = scrapy.Field()


class BursaStockItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
