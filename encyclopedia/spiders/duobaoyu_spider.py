# coding=utf-8
import re, json, inspect, sys
from ..items import EncyclopediaItem
from scrapy.http import Request
import scrapy
from scrapy.exceptions import CloseSpider
from ..common.func import *
import urlparse
from ..model.encyclopedia import *
from ..model.insurance import *
reload(sys)
sys.setdefaultencoding('utf8')
class DuobaoyuSpider(scrapy.Spider):
    name = "duobaoyu"

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
    }

    headers = '''
content-type: application/json
user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16D57 MicroMessenger/7.0.5(0x17000523) NetType/WIFI Language/zh_CN
referer: https://servicewechat.com/wx104a3cbd28a38968/15/page-frame.html
token: wx-f25c31bc-5ef7-42b5-8c4e-91fd5fb59226
accept-language: zh-cn
x-ca-stage: RELEASE
accept-encoding: br, gzip, deflate
'''

    article_detail_headers = ''''
user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16D57 MicroMessenger/7.0.5(0x17000523) NetType/WIFI Language/zh_CN miniProgram
accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
accept-language: zh-cn
accept-encoding: br, gzip, deflate
    '''

    article_list_url = 'https://api2.91duobaoyu.com/transbiz_2c/insuranceClassroom/user/categoryArticle.run?currentPage={}&pageSize={}&cid={}'
    limit = 10

    def parse_test_detail(self, response):
        print response.url
        item = EncyclopediaItem()
        item['source_url'] = response.url
        item['source'] = '多保鱼-'+ response.meta['cid'][1]
        item['title'] = response.css('#activity-name ::text').get()
        #item['category'] = response.meta['category']
        item['picture'] = response.meta['data']['coverImageUrl']
        item['content'] = response.css('#js_content').get()
        if item['content']:
            item['content'] = item['content'].replace('保鱼君', '小鲸')
            item['content'] = re.sub(r'^.*?\<p.*?\<img.*?\/p\>', '', item['content'])
        yield item

    def start_requests(self):
        self.headers = load_header_string(self.headers)
        self.article_detail_headers = load_header_string(self.article_detail_headers)

        # yield Request('https://oss.91duobaoyu.com/pythonCanvas/2019/1114/artCon/1f2865e7-d459-44d0-b6cf-da0bb32488b7.html', meta={'cid': [2,'xxx'], 'data': {'coverImageUrl': 'https://www.91duobaoyu.com/res/src/images/app-to-c/pages-webView-index/guide-img.png'}}, callback=self.parse_test_detail, headers=self.article_detail_headers)
        # return

        cids = [[27, '小白入门'], [29, '防坑指南'], [17, '重疾险专题'], [19, '寿险专题'], [18, '医疗险专题'], [20, '意外险专题'], [9, '保险公司大小'], [10, '带病投保注意事项'], [28, '社保那些事'], [22, '使用小技巧']]
        for v in cids:
            yield Request(self.article_list_url.format(1, self.limit, v[0]), meta={'cid': v}, headers=self.headers)

    def parse(self, response):
        result = json.loads(response.text)
        if not result or result['success'] is not True:
            err_log('response error', response.text)
            return
        if not result.has_key('data') or not result['data']:
            err_log('response error', result['message'])
            return
        total = result['data']['articleCount']
        if(total > 0):
            page_total = max(1, int(math.ceil(total/self.limit)))
            for page in range(1, page_total+1):
                yield Request(self.article_list_url.format(page, self.limit, response.meta['cid'][0]), meta={'cid': response.meta['cid']}, callback=self.parse_list, dont_filter=True, headers=self.headers)

    def parse_list(self, response):
        result = json.loads(response.text)
        if not result or result['success'] is not True:
            err_log('response error', response.text)
            return
        if not result.has_key('data') or not result['data']:
            err_log('response error', result['message'])
            return
        data = result['data']
        for v in data['articleList']:
            yield Request(v['articleUrl'], meta={'cid': response.meta['cid'], 'data': v}, callback=self.parse_detail, headers=self.article_detail_headers)

    def parse_detail(self, response):
        print response.url
        item = EncyclopediaItem()
        item['source_url'] = response.url
        item['source'] = '多保鱼-'+ response.meta['cid'][1]
        item['title'] = response.css('#activity-name ::text').get()
        #item['category'] = response.meta['category']
        item['picture'] = aliyun_upload_url_file(response.meta['data']['coverImageUrl'])
        item['content'] = response.css('#js_content').get()
        imgs = response.css('#js_content img::attr(src)').getall()
        for v in imgs:
            img =  aliyun_upload_url_file(v)
            item['content'] = item['content'].replace(v, img)
        if item['content']:
            item['content'] = item['content'].replace('保鱼君', '小鲸')
            item['content'] = re.sub(r'\<(section|div).*?\>[\s\n]*?\<\/(section|div)\>', '', item['content'])
            item['content'] = re.sub(r'\<p((?!\<\/p\>).)*?\<img((?!\>).)*?\.gif.*?\<\/p\>', '', item['content'])
            item['content'] = re.sub(r'\>[\s\n]*?\<', '><', item['content'])
        yield item

