# -*- coding: utf-8 -*-

from db import *
from scrapy.conf import settings
class Dlmhua(Db):
    connect_link = settings['CONNECT_LINKS']['dlmhua_spider']

