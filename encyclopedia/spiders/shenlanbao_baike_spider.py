# coding=utf-8
import re, json, inspect, sys
from ..items import EncyclopediaItem
from scrapy.http import Request
import scrapy
from scrapy.exceptions import CloseSpider
from ..common.func import *
import urlparse
reload(sys)
sys.setdefaultencoding('utf8')
class ShenlanbaoBaikeSpider(scrapy.Spider):
    name = "shenlanbao_baike"
    allowed_domains = [
        "shenlanbao.com",
    ]

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
    }

    headers = {
        'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ast;q=0.7,az;q=0.6,zh-TW;q=0.5',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'Cookie': 'sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%221726ea66759da-04d97b1a97a449-30637d06-2073600-1726ea6675aa43%22%2C%22first_id%22%3A%22%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E7%9B%B4%E6%8E%A5%E6%B5%81%E9%87%8F%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC_%E7%9B%B4%E6%8E%A5%E6%89%93%E5%BC%80%22%2C%22%24latest_referrer%22%3A%22%22%7D%2C%22%24device_id%22%3A%221726ea66759da-04d97b1a97a449-30637d06-2073600-1726ea6675aa43%22%7D; Hm_lvt_1c07eb773240afce48f029e6c8960168=1591948692,1594205603; JSESSIONID=266CDA150DC4D5C102F669B1D001AEC5; Hm_lpvt_1c07eb773240afce48f029e6c8960168=1594270907',
        'Host': 'www.shenlanbao.com',
        'Pragma': 'no-cache',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
    }
    start_urls = [
        "https://www.shenlanbao.com//wikis?typeId=1&pageSize=10&pageNo=1",
        "https://www.shenlanbao.com//wikis?typeId=2&pageSize=10&pageNo=1",
        "https://www.shenlanbao.com//wikis?typeId=3&pageSize=10&pageNo=1",
        "https://www.shenlanbao.com//wikis?typeId=4&pageSize=10&pageNo=1",
        "https://www.shenlanbao.com//wikis?typeId=5&pageSize=10&pageNo=1",
        "https://www.shenlanbao.com//wikis?typeId=6&pageSize=10&pageNo=1",
        "https://www.shenlanbao.com//wikis?typeId=7&pageSize=10&pageNo=1",
        "https://www.shenlanbao.com//wikis?typeId=9&pageSize=10&pageNo=1",
    ]

    def start_requests(self):
        for v in self.start_urls:
            yield Request(v)

    def parse(self, response):
        page_total = json.loads(response.text)['detail']['pageTotal']
        for page in range(1, page_total+1):
            yield Request(response.url.replace('pageNo=1', 'pageNo='+ str(page)), meta={'page':page}, callback=self.parse_list, dont_filter=True)

    def parse_list(self, response):
        list = json.loads(response.text)['detail']['list']
        for detail in list:
            yield Request('https://www.shenlanbao.com/baike/'+ detail['id'], callback=self.parse_detail, headers=self.headers)

    def parse_detail(self, response):
        if not response:
            print response.url
        item = EncyclopediaItem()
        item['source_url'] = response.url
        item['source'] = '深蓝保-保险百科'
        item['title'] = response.css('.encyclopedia_h3 ::text').get()
        #item['category'] = response.meta['category']
        item['picture'] = ''
        item['content'] = response.css('.encyclopedia_main div').get()
        imgs = response.css('.encyclopedia_main div img::attr(src)').getall()
        for v in imgs:
            img =  aliyun_upload_url_file(v)
            item['content'] = item['content'].replace(v, img)
        if(len(imgs)):
            item['picture'] = img + '?x-oss-process=image/resize,m_fill,h_158,w_234'
        yield item

