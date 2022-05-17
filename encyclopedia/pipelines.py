# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from model.encyclopedia import *
from model.insurance import *
from common.func import *
import json, sys

class CleaningPipeline(object):
    def process_item(self, item, spider):
        for k,v in item.items():
            if not v:
                item[k] = ''
            if k == 'title':
                item[k] = item[k].strip()
        return item

class EncyclopediaPipeline(object):
    def process_item(self, item, spider):
        model = Encyclopedia(**item)
        with Insurance(model) as db:
            db_data = db.session.query(Encyclopedia).filter(Encyclopedia.source_url==model.source_url).first()
            if db_data:
                return item

            # Shop.__table__.drop(db.engine, checkfirst=True)
            # Encyclopedia.__table__.create(db.engine, checkfirst=True)

            db.session.add(model)
        return item

