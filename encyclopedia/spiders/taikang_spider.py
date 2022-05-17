# coding=utf-8
import re, json, inspect, sys
import threading

from ..items import EncyclopediaItem
from scrapy.http import Request
import scrapy
from scrapy.exceptions import CloseSpider
from ..common.func import *
import urlparse
reload(sys)
sys.setdefaultencoding('utf8')
class TaikangSpider(scrapy.Spider):
    name = "taikang"

    custom_settings = {
        'DOWNLOAD_DELAY': 1,
    }

    headers =  '''
accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8
x-wechat-key: b95a60efdbf7a25aa074c94e9bdc52b9079b7576f1c78b3d5df1105e61ec9bd4c2fb8f159e6695882d81c8f991d23d73bb5926b8b4bc87f953bb09c3565c40a9dba187e9802f48aacd7fb13169bd2326
x-wechat-uin: NDU5NTg0NTYw
user-agent: Mozilla/5.0 (iPhone; CPU iPhone OS 12_1_4 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/16D57 MicroMessenger/7.0.5(0x17000523) NetType/WIFI Language/zh_CN
accept-language: zh-cn
accept-encoding: br, gzip, deflate
'''

    def start_requests(self):
        self.headers = load_header_string(self.headers)
        urls =[
            'https://mp.weixin.qq.com/s?__biz=MzI3NDMzNzIyMQ==&mid=2247483804&idx=1&sn=a1b5d8aee842c1281d8f96444d3e367a&chksm=eb14dd36dc635420e06fae37f620e05b3cfc8cd8f55d0a241d543082045ad65d4a895100d728&mpshare=1&scene=1&srcid=0703W90DCNApY8JcJMpW5zYx&sharer_sharetime=1593769447795&sharer_shareid=775aa7e7e187a3ec60038449d73cad7b&ascene=1&devicetype=iOS12.1.4&version=17000529&nettype=WIFI&abtest_cookie=AAACAA%3D%3D&lang=zh_CN&fontScale=100&exportkey=AUtm3uG%2BoNcT0UTVIxJ6vF4%3D&pass_ticket=jkcNeytXpJ7MbGGpNPtICeLdwbtNS6WZNoDF5wUJsmx7LZB%2BxH%2B80ICKD%2FaM%2B4UR&wx_header=1',
            'https://mp.weixin.qq.com/s?__biz=MzI3NDMzNzIyMQ==&mid=2247483792&idx=1&sn=572c4611345e5f2d17a36b1c547350d0&chksm=eb14dd3adc63542c8acae196835435964474f78abfce4206f60d1f5367e79bad7163527ebaf2&mpshare=1&scene=1&srcid=0703I9MVVLnZ3EP323IQN0cE&sharer_sharetime=1593769460046&sharer_shareid=775aa7e7e187a3ec60038449d73cad7b&ascene=1&devicetype=iOS12.1.4&version=17000529&nettype=WIFI&abtest_cookie=AAACAA%3D%3D&lang=zh_CN&fontScale=100&exportkey=AbnnxtsGTiW4kpLbbj%2BDxmk%3D&pass_ticket=jkcNeytXpJ7MbGGpNPtICeLdwbtNS6WZNoDF5wUJsmx7LZB%2BxH%2B80ICKD%2FaM%2B4UR&wx_header=1'
        ]
        for v in urls:
            yield Request(v, headers=self.headers)

    def parse(self, response):
        item = EncyclopediaItem()
        item['source_url'] = response.url
        item['source'] = '泰康之家'
        item['title'] = response.css('#activity-name ::text').get()
        #item['category'] = response.meta['category']
        item['picture'] = ''
        item['content'] = response.css('#js_content').get()
        if item['content']:
            item['content'] = item['content'].replace('点击图片 即可阅读', '').replace('visibility: hidden;', '').replace('data-src', 'src').replace('background-image:', 'bgi:').replace('background:', 'bg:').replace('二少 语录', '')
            item['content'] = re.sub(r'<img [^>]*?src="([^\>]*?wx_fmt=gif|https://mmbiz.qpic.cn/mmbiz_png/Zia1nmTN5SZY9gWzvM0CxicdiarjZHQDFawCicrWxU3rF3sDadpttAllibILmxndVBAfj1HzE2cwO17Q0xF3XW7Mv4Q/640\?wx_fmt=png)".*?>', '', item['content'])
            item['content'] = re.sub(r'点击“阅读原文”.*?<', '<', item['content'].encode())
            item['content'] = re.sub(r'<section[^>]*?><section[^>]*?data-tools="新媒体排版".*?</section>.*?</section>', '', item['content'].encode())
            item['content'] = re.sub(r'<span class="js_jump_icon h5_image_link".*?</span>', '', item['content'])
            # 去除空内容标签
            pattern = r'\<(((?!p\s)[a-z])+)[^\>]*?\>[\s\n ]*?\<\/\1\>'
            while(re.search(pattern, item['content'])):
                item['content'] = re.sub(pattern, '', item['content'])
            # 去除内容中多余的空格或换行
            item['content'] = re.sub(r'\>[\s\n]*?\<', '><', item['content'])
            # 提取图片
            compile = re.compile('<img [^\>]*?src="(.*?)"', re.I)
            imgs = re.findall(compile, item['content'])
            # compile = re.compile('background:[ ]*url\("(.*?)"\)', re.I)
            # imgs = imgs + re.findall(compile, item['content'])
            # imgs = response.css('#js_content img::attr(data-src)').getall()
            # 上传与替换图片
            def upload_and_replace(v, lock, retry = 0):
                try:
                    img = aliyun_upload_url_file(v)
                    # 随机设置一张图片为陈列图
                    if random.randint(0, 10) > 7 or not item['picture']:
                        item['picture'] = img + '?x-oss-process=image/resize,m_fill,h_158,w_234'
                    with lock:
                        lock.acquire()
                        item['content'] = item['content'].replace(v, img)
                        lock.release()
                except:
                    retry = retry + 1
                    if retry > 2:
                        print '重试上传失败'
                        return
                    print v,
                    upload_and_replace(v, lock, retry)
            if imgs:
                lock = threading.Condition()
                threads = []
                for v in imgs:
                    t= threading.Thread(target=upload_and_replace, args=(v, lock))
                    # t.setDaemon(False) #False:等待子线程完成
                    t.start()
                    threads.append(t)
                    time.sleep(1)
                for t in threads:
                    t.join()
        yield item


