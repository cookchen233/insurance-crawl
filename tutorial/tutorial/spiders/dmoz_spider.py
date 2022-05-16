# coding=utf-8
import re, json, inspect, sys
from tutorial.items import DmozItem
from scrapy.http import Request
import scrapy
from scrapy.exceptions import CloseSpider
from tutorial.common.func import *
import urlparse
from selenium import webdriver
from selenium.webdriver.common.proxy import ProxyType
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
reload(sys)
sys.setdefaultencoding('utf8')
class DmozSpider(scrapy.Spider):
    name = "dmoz"
    allowed_domains = [
        "dmoz.org",
        'huaji.com'
    ]
    start_urls = [
        # "https://www.jd.com",
        "https://www.huaji.com/index/findshop",
        #"http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/"
    ]

    source = 'huaji.com'

    def parse(self, response):
        for page in range(0, 500):
            log('parse_count', page)
            try:
                page_url = 'https://www.huaji.com/index/findshop?page={}'.format(page)
                yield Request(page_url, meta={'page':page}, callback=self.parse_list, dont_filter=True)
            except Exception, e:
                log(sys._getframe().f_code.co_name, str(e), page_url)
                raise CloseSpider('{}, {}, {}'.format(sys._getframe().f_code.co_name, str(e), page_url))

    def parse_list(self, response):
        log('parse_list_count', response.url)
        # 当列表返回空内容时, 使用selenium模拟人工点击证明身份, 循环5次
        if len(response.css('.search-item')) < 3:
            if not 'count' in response.meta:
                response.meta['count'] = 1
            if response.meta['count'] < 6:
                if response.meta['count'] == 1:
                    log('empty_content', len(response.css('.search-item')), response.url, response.css('.search-container').get())
                self._page_click(response.url)
                yield Request(response.url, meta={'count': response.meta['count'] + 1}, callback=self.parse_list, dont_filter=True)
            else:
                log('finally_empty_content', len(response.css('.search-item')), response.url, response.css('.search-container').get())
                raise CloseSpider('finally_empty_content, {}, {}, {}'.format(len(response.css('.search-item')), response.url, response.css('.search-container').get()))
        else:
            for list in response.css('.search-item'):
                item = DmozItem()
                item['source'] = self.source
                item['source_url'] = response.url
                item['name'] = list.css('.search-header .search-title a:nth-child(2)::text').get()
                item['shop_url'] = list.css('.search-header .search-title a:nth-child(2)::attr(href)').extract_first()
                # item['shop_url'] = urlparse.urljoin(response.url, item['shop_url'].strip())
                item['shop_url'] = response.urljoin(item['shop_url'])
                # item['qq'] = re.search(r'uin=(.*?)&',list.css('.search-title a:nth-child(3)::attr(href)').extract()[0]).group(1)
                item['qq'] = list.css('.search-header .search-title a:nth-child(3)::attr(href)').re_first(
                    r'uin=(.*?)&')
                item['tel'] = list.css('.search-body .copytel::text').extract_first()
                item_none = self.check_none(item)
                if item_none:
                    log('item_none', item_none, response.css('.search-container').get(), len(response.css('.search-item')))
                    raise CloseSpider('item_none {}, {} {}'.format(item_none, response.css('.search-container').get(), len(response.css('.search-item'))))
                yield Request(item['shop_url'], meta={'item': item}, callback=self.parse_detail,dont_filter=False)


    def parse_detail(self, response):
        log('parse_detail_count', response.url)
        item = response.meta['item']
        area = response.css('.shop-profile dl dd:nth-child(4)::text').get().split('|')
        item['province'] = area[0].strip()
        item['city'] = area[1].strip()
        item['origin_address'] = response.css('.profile dl dd:nth-child(12)::text').get()
        if item['origin_address'] is None:
            item['origin_address'] = response.css('.shop-gallery dl dd:nth-child(12)::text').get()
        # print '---------------------' + self.__class__.__name__ + '.' + sys._getframe().f_code.co_name + '--------------------'
        # print js on.dumps(dict(item), ensure_ascii=False, indent=4)
        yield item

    def _page_click(self, url, proxy=None):
        options = webdriver.ChromeOptions()
        options.add_argument('headless')  # 静默模式
        if proxy:
            options.add_argument('--proxy-server={}'.format(proxy))
        driver = webdriver.Chrome(
            executable_path='/usr/local/bin/chromedriver',
            chrome_options=options
        )
        driver.get(url)
        # print '-------------------------------------------------source'
        # print(driver.page_source)
        # print '-------------------------------------------------source-end'
        driver.execute_script('window.scrollTo(0,document.body.scrollHeight)')  # 模拟鼠标滚到最低
        element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "pagination"))
        )
        try:
            # element.find_element_by_css_selector('a[data-page=\'{}\']'.format(page)).click()
            element.find_element_by_css_selector('.layui-laypage-btn').click()
            driver.quit()
        except Exception, e:
            log(sys._getframe().f_code.co_name, str(e), element.get_attribute('outerHTML'))
            raise CloseSpider('{}, {}, {}'.format(sys._getframe().f_code.co_name, str(e), element.get_attribute('outerHTML')))

    def check_none(self, item):
        allowed = ['qq', 'tel']
        for k in item:
            if not k in allowed and item[k] is None:
                return k
        return False

