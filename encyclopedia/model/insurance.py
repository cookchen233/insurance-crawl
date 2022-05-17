# -*- coding: utf-8 -*-

from db import *
from scrapy.conf import settings
class Insurance(Db):
    connect_link = settings['CONNECT_LINKS']['insurance']

