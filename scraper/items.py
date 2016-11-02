# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class UserItem(scrapy.Item):
    created_at = scrapy.Field()
    user       = scrapy.Field()
    listings   = scrapy.Field()
    reviews    = scrapy.Field()
    pass
