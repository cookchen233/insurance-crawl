# coding=utf-8
import re, json, inspect, sys

import os
import urllib
import uuid

from pytesseract import pytesseract
from tutorial.items import DmozItem
from scrapy.http import Request
import scrapy
from scrapy.exceptions import CloseSpider
from tutorial.common.func import *
from tutorial.common.const import *
import urlparse
from selenium import webdriver
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image,ImageEnhance
from tutorial.model.dlmhua import *
from tutorial.model.shop import *
reload(sys)
sys.setdefaultencoding('utf8')
class DmozSpider(scrapy.Spider):

    name = "zhuandan"
    allowed_domains = [
        "dmoz.org",
        'huaji.com',
        'zhuandan.com'
    ]
    start_urls = [
        "http://www.zhuandan.com/Stores/flowers",
    ]

    source = 'zhuandan.com'

    _chrome_driver = None

    def parse(self, response):
        model = Shop()
        with Dlmhua(model) as db:
            Shop.__table__.drop(db.engine, checkfirst=True)
            Shop.__table__.create(db.engine, checkfirst=True)

        try:
            total_page = response.css('.zdb-page .end::attr(href)').re_first(r'p=(.*)')
            total_page = min(5000, int(total_page))
            for page in range(1, total_page + 1):
                page_url = 'http://www.zhuandan.com/Stores/flowers?&p={}'.format(page)
                yield Request(page_url, callback=self.parse_list, dont_filter=True)
        except Exception, e:
            raise CloseSpider('\n'.join(err_log()))

    def parse_list(self, response):
        try:
            for list in response.css('.s-itemlist .item'):
                item = DmozItem()
                item['source'] = self.source
                item['source_url'] = response.url
                item['name'] = list.css('.title a::text').get()
                item['shop_url'] = list.css('.title a::attr(href)').extract_first()
                item['shop_url'] = response.urljoin(item['shop_url'])
                # item['qq'] = re.search(r'uin=(.*?)&',list.css('.search-title a:nth-child(3)::attr(href)').extract()[0]).group(1)
                item['qq'] = ','.join(list.css('.QQConsulting::attr(data-qq)').getall())
                tel_img_url = response.urljoin(list.css('.col-4 p img::attr(src)').get())
                try:
                    tel_file = save_img(tel_img_url)
                except Exception, e:
                    tel_file = self._save_tel(tel_img_url)
                try:
                    im = Image.open(tel_file)
                    im = im.convert("RGBA")
                    enhancer = ImageEnhance.Color(im)
                    enhancer = enhancer.enhance(0)
                    enhancer = ImageEnhance.Brightness(enhancer)
                    enhancer = enhancer.enhance(2)
                    enhancer = ImageEnhance.Contrast(enhancer)
                    enhancer = enhancer.enhance(8)
                    enhancer = ImageEnhance.Sharpness(enhancer)
                    im = enhancer.enhance(20)
                    item['tel'] = pytesseract.image_to_string(im, config='--psm 7 -c tessedit_char_whitelist=abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                except Exception, e:
                    err_log(list.get(), response.url)
                address = list.css('.col-2 :nth-child(2) + p a::attr(href)').re_first(r'q=(.*)')
                address = urllib.unquote(address)
                item['origin_address'] = address[address.find(' ')+1:]
                area = address[:address.find(' ')].split('|')
                item['province'] = area[0]
                if len(area) > 1:
                    item['city'] = area[1]
                else:
                    item['city'] = item['province']
                if len(area) > 2:
                    item['district'] = area[2]
                else:
                    item['district'] = item['city']
                item_none = self.check_none(item)
                if item_none:
                    raise CloseSpider('\n'.join(log('item_none', item_none, response.css('.s-itemlist').get(), list.get(), response.url)))
                yield item
        except Exception, e:
            raise CloseSpider('\n'.join(err_log(response.css('.s-itemlist').get(), response.url)))

    def _save_tel(self, url):
        driver = self._get_chrome_driver()
        driver.get(url)
        # print '-------------------------------------------------source'
        # print(driver.page_source)
        # print '-------------------------------------------------source-end'
        scheight = .1
        while scheight < 9.9:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight/%s);" % scheight)
            scheight += .01
        path = Const.DATA_PATH + '/selenium-tel/'
        if not os.path.exists(path):
            os.makedirs(path)
        filename = '{}/{}.png'.format(path, uuid.uuid1())
        driver.save_screenshot(filename)
        driver.quit()
        return filename

    def check_none(self, item):
        allowed = ['qq', 'tel']
        for k in item:
            if not k in allowed and item[k] is None:
                return k
        return False

    def _get_chrome_driver(self, proxy=None):
        if not self._chrome_driver:
            options = webdriver.ChromeOptions()
            options.add_argument('headless')  # 静默模式
            if proxy:
                options.add_argument('--proxy-server={}'.format(proxy))
            self._chrome_driver = webdriver.Chrome(
                executable_path='/usr/local/bin/chromedriver',
                chrome_options=options
            )
        return self._chrome_driver

