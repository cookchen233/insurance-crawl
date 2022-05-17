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
class ShenlanbaoSpider(scrapy.Spider):
    name = "shenlanbao"

    allowed_domains = [
        "shenlanbao.com",
    ]

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
    }

    headers =  '''
cookie: token=eyJhbGciOiJIUzI1NiJ9.eyJqdGkiOiI1MjM2QSIsInN1YiI6IntcImNyZWF0ZV90aW1lXCI6MTU5NDM0OTk0NzAwMCxcImlkXCI6XCIxMjAwNzEwMTA1OTA3MjAxMDFcIixcImxvZ2luX3RpbWVcIjoxNTk0NjEwMDk3MDI0LFwib3BlbmlkXCI6XCJvUXhjTjVHZnpJbVh1d0xfVHQzWjF2WHZhOVh3XCIsXCJ1bmlvbmlkXCI6XCJcIn0iLCJpYXQiOjE1OTQ2MTAwOTcsImV4cCI6MTU5NDg2OTI5N30.2EoHPlUJlgtgGLZq_J5pS2_vJ2Z35-jAg_G43mp2i-E
accept: */*
content-type: application/json
accept-encoding: br, gzip, deflate
user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16D57 MicroMessenger/7.0.5(0x17000523) NetType/WIFI Language/zh_CN
referer: https://servicewechat.com/wxb64c65d1ca399033/85/page-frame.html
accept-language: zh-cn
    '''

    limit =10

    def start_requests(self):
        self.headers = load_header_string(self.headers)

        cids = [['10001', '入门必读'], ['10002', '投保指南'], ['10003', '理赔科普'], ['10005', '防坑指南'], ['10006', '社保医保'], ['10007', '保险公司'], ['10008', '车险理赔']]
        for v in cids:
            yield Request('https://weapp-api.shenlanbao.com/insure/column/{}'.format(v[0]), meta={'cid': v}, headers=self.headers)

    def parse(self, response):
        result = json.loads(response.text)
        if not result or result['code'] != 0:
            err_log('response error', response.text)
            return
        for v in result['detail']['labels']:
            total = v['allCount']
            if(total > 0):
                page_total = max(1, int(math.ceil(total/self.limit)))
                for page in range(1, page_total+1):
                    yield Request('https://weapp-api.shenlanbao.com/insure/content/{}?pageNo={}&pageSize={}'.format(v['id'], page, self.limit), meta={'cid': response.meta['cid']}, callback=self.parse_list, dont_filter=True, headers=self.headers)

    def parse_list(self, response):
        result = json.loads(response.text)
        if not result or result['code'] != 0:
            err_log('response error', response.text)
            return
        for v in result['detail']:
            yield Request('https://weapp-api.shenlanbao.com/api/weappArticleDetailNewByIdPortalNew?id={}'.format(v['referId']), meta={'cid': response.meta['cid']}, callback=self.parse_detail, dont_filter=True, headers=self.headers)

    def parse_detail(self, response):
        result = json.loads(response.text)
        if not result or result['code'] != 0:
            err_log('response error', response.text)
            return
        if not result.has_key('detail'):
            err_log('response error', response.meta['cid'][1], response.url, result['msg'])
            return
        data = result['detail']
        item = EncyclopediaItem()
        item['source_url'] = response.url
        item['source'] = '深蓝保-'+ response.meta['cid'][1]
        item['title'] = data['title']
        #item['category'] = response.meta['category']
        item['picture'] = aliyun_upload_url_file(data['cover_url'])
        item['content'] = self.node_to_html(json.loads(data['wx_content']))
        compile = re.compile('<img.*?src="(.*?)"', re.I)
        imgs = re.findall(compile, item['content'])
        for v in imgs:
            img =  aliyun_upload_url_file(v)
            item['content'] = item['content'].replace(v, img)
        yield item


    def node_to_html(self, node):
        wxml = ''
        if node['node'] == 'element':
            wxml += '<{}'.format(node['tag'])
            if node.has_key('attr'):
                for k, v in node['attr'].items():
                    attrs = ''.join(v)
                    wxml += ' {}="{}"'.format(k, attrs)

            if node['tag'] == 'img':
                wxml += ' />'
            else:
                wxml += '>'
                if node.has_key('nodes'):
                    for v in node['nodes']:
                        wxml += self.node_to_html(v)
                wxml += '</{}>'.format(node['tag'])
        elif node['node'] == 'text':
            for v in node['textArray']:
                wxml += v[v['node']]
        else:
            wxml += '<{}>'.format(node['node'])
            if node.has_key('nodes'):
                for v in node['nodes']:
                    wxml += self.node_to_html(v)
            wxml += '</{}>'.format(node['node'])
        return wxml