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
from PIL import Image, ImageEnhance, ImageFilter
from tutorial.model.dlmhua import *
from tutorial.model.shop import *
reload(sys)
sys.setdefaultencoding('utf8')
class DmozSpider(scrapy.Spider):

    name = "huawa"
    allowed_domains = [
        "dmoz.org",
        'huaji.com',
        'zhuandan.com'
        'huawa.com'
    ]
    start_urls = [
        "http://www.huawa.com/store",
    ]

    source = 'huawa.com'

    _chrome_driver = None

    def parse(self, response):
        # add = [
        #     ('新疆 巴音郭楞州 库尔勒市', 'sdfsdf'),
        #     ('新疆 阿克苏地区 阿克苏市', '阿克苏市步行街29号'),
        #     ('新疆 喀什地区 喀什市', '环疆山陆林楼下鲜花店'),
        #     ('新疆 乌鲁木齐市 新市区', '环疆山陆林楼下鲜花店'),
        #     ('新疆 伊犁州 伊宁市', '伊宁市友谊路1'),
        #     ('新疆 昌吉州 昌吉市', '昌吉市健康东路156号兰世牛'),
        #     ('广西省 桂林市 恭城瑶族自治县', '万家福'),
        #     ('广西省 防城港市 防城区', '万家福'),
        #     ('北京市', '北京市丰台区南四环中路2'),
        #     ('吉林省 吉林市 丰满区', '丰满区恒山西路24号'),
        #     ('北京市 朝阳区', '区南四环中路2'),
        #     ('重庆市开县', '水电费水电费2'),
        #     ('内蒙古 呼和浩特市 武川县', '青山路粮食局旁蓉蓉花店(粮食局旁)'),
        #     ('贵州省 遵义市 绥阳县', '新市路凤凰苑斜对面')
        # ]
        # for a in add:
        #     # print a
        #     aa=self._get_area(a[0], a[1])
        #     print json.dumps(aa,ensure_ascii=False)
        #     # bb=self._get_area(a[1], a[0])
        #     # print json.dumps(bb,ensure_ascii=False)
        # s
        model = Shop()
        with Dlmhua(model) as db:
            Shop.__table__.drop(db.engine, checkfirst=True)
            Shop.__table__.create(db.engine, checkfirst=True)
        try:
            total_page = response.css('.pagination li:last-child a::attr(href)').re_first(r'-([0-9]+)\.htm')
            total_page = min(10000, int(total_page))
            for page in range(1, total_page):
                page_url = 'http://www.huawa.com/store-0-0-0-0-0-0-0-0-{}.html'.format(page)
                yield Request(page_url, headers={'X-Requested-With': 'XMLHttpRequest'}, callback=self.parse_list, dont_filter=True)
        except Exception, e:
            raise CloseSpider('\n'.join(err_log()))

    def parse_list(self, response):
        try:
            for list in response.css('.store_n li'):
                item = DmozItem()
                item['source'] = self.source
                item['source_url'] = response.url
                item['name'] = list.css('.diqu b a::text').get()
                item['shop_url'] = list.css('.diqu b a::attr(href)').get()
                item['shop_url'] = response.urljoin(item['shop_url'])
                # item['qq'] = re.search(r'uin=(.*?)&',list.css('.search-title a:nth-child(3)::attr(href)').extract()[0]).group(1)
                item['qq'] = list.css('.store_dec .desc p:nth-child(2) a::attr(href)').re_first(r'uin=(.*?)&')
                tel_img_urls = list.css('.store_dec .desc p img[align="absmiddle"]::attr(src)').getall()
                item['tel'] = ''
                item['img_tel'] = ','.join(tel_img_urls)
                tels = []
                try:
                    for url in tel_img_urls:
                        if url:
                            tels.append(self._get_tel(url))
                    item['tel'] = ','.join(tels)
                except Exception, e:
                    err_log(list.get(), response.url)
                item['origin_address'] = list.css('.store_dec .desc .adress::text').get().replace(u'花店地址：', '')
                area = list.css('.diqu::text').get().replace('[', '').replace(']', '')
                item.update(self._get_area(item['origin_address'], area))
                item_none = self.check_none(item)
                if item_none:
                    raise CloseSpider('\n'.join(log('item_none', item_none, list.get(), response.url)))
                yield item
        except Exception, e:
            raise CloseSpider('\n'.join(err_log(list.get(), response.url)))

    def _get_area(self, address, address2):
        result = {'province': '', 'city': '', 'district': ''}
        address = address.replace(' ', '')
        address2 = address2.replace(' ', '')
        with open(Const.RESOURCE_PATH + 'area/province.json', 'r') as f:
            province_data = json.loads(f.read())
        with open(Const.RESOURCE_PATH + 'area/city.json', 'r') as f:
            city_data = json.loads(f.read())
        with open(Const.RESOURCE_PATH + 'area/district.json', 'r') as f:
            district_data = json.loads(f.read())
        def multi_replace(multi_search, replace, str):
            for search in  multi_search:
                if str.find(search) == 0:
                    str = str.replace(search, replace, 1)
                    if str.find(search) == 0:
                        str = str.replace(search, replace, 1)
                    break
            return str
        def multi_find(multi_search, str, min_pos):
            pos = []
            if min_pos > -1:
                pos.append(min_pos)
            for search in  multi_search:
                if search and str.find(search) != -1:
                    pos.append(str.find(search))
            if len(pos) < 1:
                return -1
            return min(pos)
        def get_city(province, address, address2):
            p_name = province['name'].decode('utf8')[0:2].encode('utf8')
            address = multi_replace([province['name'], p_name], '', address )
            address2  = multi_replace([province['name'], p_name], '', address2)
            pos =  -1
            for cn in city_data[province['code']]:
                city = city_data[province['code']][cn]
                if len(city['name'].decode('utf8')) < 2:
                    continue
                c_name = city['name'].decode('utf8')[0:2].encode('utf8')
                pos1 = multi_find([city['name'], c_name], address, pos)
                pos2 = multi_find([city['name'], c_name], address2, pos1)
                if pos2 != -1:
                    if pos == -1 or pos2 < pos:
                        pos = pos2
                        result['city'] = city['name']
                        get_district(city, address, address2)

            if not result['city']:
                for cn in city_data[province['code']]:
                    city = city_data[province['code']][cn]
                    get_district(city, address, address2)
                    if result['district']:
                        result['city'] = city['name']
                        break


        def get_district(city,address,address2):
            c_name = city['name'].decode('utf8')[0:2].encode('utf8')
            address = multi_replace([city['name'], c_name], '', address )
            address2  = multi_replace([city['name'], c_name], '', address2)
            if len(district_data[city['code']]) == 1:
                district = district_data[city['code']]['0']
                result['district'] = district['name']
            else:
                pos = -1
                for dn in district_data[city['code']]:
                    district = district_data[city['code']][dn]
                    d_name = district['name'].decode('utf8')[0:2].encode('utf8')
                    pos1 = multi_find([district['name'], d_name], address, pos)
                    pos2 = multi_find([district['name'], d_name], address2, pos1)
                    if pos2 != -1:
                        if pos == -1 or pos2 < pos:
                            pos = pos2
                            result['district'] = district['name']

        pos = -1
        for pn in province_data:
            province = province_data[pn]
            p_name = province['name'].decode('utf8')[0:2].encode('utf8')
            pos1 = multi_find([province['name'], p_name], address, pos)
            pos2 = multi_find([province['name'], p_name], address2, pos1)
            if pos2 != -1:
                if pos == -1 or pos2 < pos:
                    pos = pos2
                    result['province'] = province['name']
                    get_city(province, address, address2)
        for k in result:
            if not result[k]:
                result[k] = ''
        return result


    def _get_tel(self, url):
        try:
            filename = save_img(url)
        except Exception, e:
            path = Const.DATA_PATH + '/selenium-tel/'
            if not os.path.exists(path):
                os.makedirs(path)
            driver = self._get_chrome_driver()
            driver.get(url)
            # print '-------------------------------------------------source'
            # print(driver.page_source)
            # print '-------------------------------------------------source-end'
            scheight = .1
            while scheight < 9.9:
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight/%s);" % scheight)
                scheight += .01
            filename = '{}/{}.jpg'.format(path, uuid.uuid1())
            driver.save_screenshot(filename)
            driver.quit()
        im = Image.open(filename)
        tel = self.enhance_a(im)
        if len(tel) < 11 or tel.find('1') != 0:
            tel = self.enhance_b(im)
        return tel

    def enhance_a(self, im):
        im.convert("RGBA")
        enhancer = ImageEnhance.Color(im)
        enhancer = enhancer.enhance(0)
        enhancer = ImageEnhance.Brightness(enhancer)
        enhancer = enhancer.enhance(2)
        enhancer = ImageEnhance.Contrast(enhancer)
        enhancer = enhancer.enhance(8)
        enhancer = ImageEnhance.Sharpness(enhancer)
        im = enhancer.enhance(20)
        str = pytesseract.image_to_string(im, config='--psm 7 -c tessedit_char_whitelist=0123456789')
        return ''.join(str.split())

    def enhance_b(self, im):
        im.convert("RGBA")
        im = ImageEnhance.Contrast(im)
        im = im.enhance(1.2)
        im = ImageEnhance.Color(im)
        im = im.enhance(0.8)

        im = ImageEnhance.Brightness(im)
        im = im.enhance(1.4)

        im = ImageEnhance.Contrast(im)
        im = im.enhance(0.1)

        im = ImageEnhance.Sharpness(im)
        im = im.enhance(20)
        str = pytesseract.image_to_string(im, config='--psm 7 -c tessedit_char_whitelist=0123456789')
        return ''.join(str.split())

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

