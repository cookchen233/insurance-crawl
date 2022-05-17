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
class DuobaoyuCidianSpider(scrapy.Spider):
    name = "duobaoyu_cidian"

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
    }

    headers =  '''
content-type: application/json
user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16D57 MicroMessenger/7.0.5(0x17000523) NetType/WIFI Language/zh_CN
referer: https://servicewechat.com/wx104a3cbd28a38968/15/page-frame.html
token: wx-f25c31bc-5ef7-42b5-8c4e-91fd5fb59226
accept-language: zh-cn
x-ca-stage: RELEASE
accept-encoding: br, gzip, deflate
'''

    def start_requests(self):
        self.headers = load_header_string(self.headers)
        url ='https://api2.91duobaoyu.com/transbiz_2c/insuranceClassroom/user/userLexicons.run'
        yield Request(url, headers=self.headers)

    def parse(self, response):
        result = json.loads(response.text)
        if not result or result['success'] is not True:
            err_log('response error', response.text)
            return
        for v in result['data']['lexiconTypes']:
            if v['lexicons']:
                for v1 in v['lexicons']:
                    yield Request('https://api2.91duobaoyu.com/transbiz_2c/insuranceClassroom/user/lexiconDetail.run?lexiconId='+ str(v1['lexiconId']), callback=self.parse_detail, dont_filter=True, headers=self.headers)

    def parse_detail(self, response):
        result = json.loads(response.text)
        if not result or result['success'] is not True:
            err_log('response error', response.text)
            return
        data = result['data']
        item = EncyclopediaItem()
        item['source_url'] = response.url
        item['source'] = '多保鱼-保险词典'
        item['title'] = data['lexiconName']
        #item['category'] = response.meta['category']
        item['picture'] = ''
        item['content'] = '<p>{}</p>'.format(data['description'])
        for v in data['explanationList']:
            item['content'] += '<p><strong>{}</strong></p><p>{}</p>'.format(v['title'], v['content'])
        compile = re.compile('<img.*?src="(.*?)"', re.I)
        imgs = re.findall(compile, item['content'])
        for v in imgs:
            img =  aliyun_upload_url_file(v)
            item['content'] = item['content'].replace(v, img)
        if(len(imgs)):
            item['picture'] = img + '?x-oss-process=image/resize,m_fill,h_158,w_234'
        yield item

