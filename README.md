# airbnb-scraper

An Airbnb scraper built using Scrapy

## How to

To run this project you will need to:

1. Fill the method `user_ids_to_download` at airbnb_spider.py with the strategy you need to download the data (*as a list of ids coming from a CSV file*).
2. Extract an `airbnb_client_id` from a device using the Airbnb unofficial API (*as an Android phone with the official app*). Create a enviroment variable called `AIRBNB_CLIENT_ID` with the value of such key.
3. Execute `scrapy crawl airbnb`.

