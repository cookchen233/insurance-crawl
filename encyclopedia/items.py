# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class EncyclopediaItem(scrapy.Item):
    # define the fields for your item here like:
    title = scrapy.Field()
    #category = scrapy.Field()
    picture = scrapy.Field()
    source_url = scrapy.Field()
    source = scrapy.Field()
    content = scrapy.Field()
