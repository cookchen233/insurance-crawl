# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

from model.dlmhua import *
from model.shop import *
from common.func import *
import json, sys

class FormatPipeline(object):

    def __init__(self):
        self.name_and_tel = set()

    def process_item(self, item, spider):
        key = (item['name'], item['tel'])
        if key in self.name_and_tel:
            log('repeat_item', json.dumps(dict(item)))
            return False
        else:
            self.name_and_tel.add(key)
        try:
            for k in item:
                if item[k] is None:
                    log('format_item_none', k, item['source_url'], item['shop_url'])
                # if type(value) == str: # it's unicode
                if isinstance(item[k], basestring):
                    item[k] = "".join(item[k].split())
            address = item['origin_address']
            if not 'district' in item:
                address = item['origin_address'].replace(item['province'], '').replace(item['city'], '')
                if item['city'].find(u'区') != -1:
                    item['district'] = item['city']
                    item['city'] = item['province']
                else:
                    pos = address.find(u'县')
                    if pos == -1:
                        pos = address.find(u'区')
                        if pos == -1:
                            pos = address.find(u'市')
                    if pos != -1:
                        item['district'] = address[:pos + 1]
                    else:
                        item['district'] = item['city']
            item['address'] = address.replace(item['province'] + '市', '')\
                .replace(item['province'] + '省', '')\
                .replace(item['province'], '')\
                .replace(item['city'] + '市', '')\
                .replace(item['city'], '')\
                .replace(item['district'] + '区', '')\
                .replace(item['district'], '')
        except Exception, e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            file = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log(sys._getframe().f_code.co_name, file, exc_tb.tb_lineno, exc_type, str(e), json.dumps(dict(item)))
        # print '---------------------'+ self.__class__.__name__ +'.'+ sys._getframe().f_code.co_name +'--------------------'
        # print json.dumps(dict(item), ensure_ascii=False, indent=4)
        return item

class TutorialPipeline(object):

    def process_item(self, item, spider):
        model = Shop(**item)
        with Dlmhua(model) as db:
            # Shop.__table__.drop(db.engine, checkfirst=True)
            Shop.__table__.create(db.engine, checkfirst=True)
            print model.ctime
            db.session.add(model)
        return item


