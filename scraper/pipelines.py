# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os

class JsonWriterPipeline(object):
    def process_item(self, item, spider):
        user_id_str = str(item['user']['id'])
        folder = 'output/%s' % '/'.join(list(user_id_str))
        if not os.path.exists(folder): os.makedirs(folder)
        filename = '%s/user_%s.json' % (folder, user_id_str)
        with open(filename, 'w+') as f: json.dump(dict(item), f)
        return item
