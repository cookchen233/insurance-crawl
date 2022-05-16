# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field, Spider,item


def strip(self, value):
    return value.strip()
class TutorialItem(Item):
    # define the fields for your item here like:
    # name = Field()
    pass

class DmozItem(Item):

    name = Field()
    qq = Field()
    tel = Field()
    img_tel = Field()
    address = Field()
    province = Field()
    city = Field()
    district = Field()
    origin_address = Field()
    source_url = Field()
    shop_url = Field()
    source = Field()