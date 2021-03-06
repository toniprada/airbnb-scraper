import scrapy
import json
import time
import csv
from scraper.items import UserItem
from scraper import settings
from airbnbpy.request_builder import AirbnbRequestBuilder

class AirbnbSpider(scrapy.Spider):
    name = "airbnb"
    allowed_domains = ["api.airbnb.com"]

    def __init__(self, *args, **kwargs):
        super(AirbnbSpider, self).__init__(*args, **kwargs)
        self.airbnb = AirbnbRequestBuilder(settings.AIRBNB_CLIENT_ID)
        self.start_urls = [self.airbnb.user(user_id)['url'] for user_id in self.user_ids_to_download()]

    def user_ids_to_download(self):
        return ['1']

    def parse(self, response):
        user = json.loads(response.body)['user']
        # got data
        url = self.airbnb.user_owned_listings(user['id'])['url']
        request = scrapy.Request(url, callback=self.parse_listings)
        request.meta['user_id'] = user['id']
        request.meta['user']    = user
        yield request

    def parse_listings(self, response):
        user_id  = response.meta['user_id']
        user     = response.meta['user']
        # got data
        listings_ids = [listing['id'] for listing in json.loads(response.body)['listings']]
        if len(listings_ids) > 0:
            # it has owned listings. pop first one and parse it
            url = self.airbnb.listing(listings_ids.pop())['url']
            request = scrapy.Request(url, callback=self.parse_listing)
            request.meta['user_id']      = user['id']
            request.meta['user']         = user
            request.meta['listings']     = []
            request.meta['listings_ids'] = listings_ids # paginating
            yield request
        else:
            # no owned listings, go to parse reviews
            url = self.airbnb.user_reviews(user_id)['url']
            request = scrapy.Request(url, callback=self.parse_reviews_paginate)
            request.meta['user_id']  = user['id']
            request.meta['user']     = user
            request.meta['listings'] = []
            yield request

    def parse_listing(self, response):
        user_id      = response.meta['user_id']
        user         = response.meta['user']
        listings_ids = response.meta['listings_ids'] # paginating
        listings     = response.meta['listings']
        listings.append(json.loads(response.body)['listing'])
        # got data
        if len(listings_ids) > 0:
            # it has MORE owned listings. parse next one
            url = self.airbnb.listing(listings_ids.pop())['url']
            request = scrapy.Request(url, callback=self.parse_listing)
            request.meta['user_id']      = user['id']
            request.meta['user']         = user
            request.meta['listings_ids'] = listings_ids
            request.meta['listings']     = listings
            yield request
        else:
            # no more owned listings, go to parse reviews
            url = self.airbnb.user_reviews(user_id)['url']
            request = scrapy.Request(url, callback=self.parse_reviews_paginate)
            request.meta['user_id']  = user['id']
            request.meta['user']     = user
            request.meta['listings'] = listings
            yield request

    def parse_reviews_paginate(self, response):
        user_id  = response.meta['user_id']
        user     = response.meta['user']
        listings = response.meta['listings']
        offset   = response.meta['offset'] if ('offset' in response.meta) else 0
        reviews  = json.loads(response.body)['reviews']
        # got saved data
        if (len(reviews) > 49): # limited, paginate to get more
            if 'reviews' in response.meta: reviews =  response.meta['reviews'] + reviews
            offset += 50
            url = self.airbnb.user_reviews(user_id, offset=offset)['url']
            request = scrapy.Request(url, callback=self.parse_reviews_paginate)
            request.meta['user_id']  = user['id']
            request.meta['user']     = user
            request.meta['listings'] = listings
            request.meta['offset']   = offset
            request.meta['reviews']  = reviews
            yield request
        else:
            if 'reviews' in response.meta: reviews =  response.meta['reviews'] + reviews
            item = UserItem()
            item['created_at'] = time.time()
            item['user']       = user
            item['listings']   = listings
            item['reviews']    = reviews
            yield item
