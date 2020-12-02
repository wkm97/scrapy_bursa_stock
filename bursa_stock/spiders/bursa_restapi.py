import scrapy
import json
from ..items import HistoricalDataItem
import random
import logging
import re
from ..tools.fixBursaCode import fixBursaCode

class BursaMalaysiaHistoricalDataSpider(scrapy.Spider):
    name = 'bursa_malaysia_ticker_data'
    bursa_malaysia_url = 'https://www.bursamalaysia.com/trade/trading_resources/listing_directory/company-profile?stock_code={}'
    source = 'bursa_malaysia'
    custom_settings = {
        'ITEM_PIPELINES': {
            'bursa_stock.pipelines.BursaStockPipeline': 300,
        }
    }

    def start_requests(self):
        print(self)
        arg_bursacode = self.bursacode
        yield scrapy.Request(
            self.bursa_malaysia_url.format(arg_bursacode),
            )
    
    def parse(self, response):
        # /section[2]/div/div/div[2]/div/div/div
        stockcode = response.xpath("//div[@id='stockChartContainer']/@data-stock-code")[0].extract()
        api_source = response.xpath("//div[@id='stockChartContainer']/@data-api-source")[0].extract()
        ws_a = response.xpath("//div[@id='stockChartContainer']/@data-ws-a")[0].extract()
        ws_m = response.xpath("//div[@id='stockChartContainer']/@data-ws-m")[0].extract()
        random_year = 2020 #random.randint(2010, 2014)
        request_url = 'https:' + api_source + '?stock_code={}'.format(stockcode) + '&mode=historical&from_date={}0428&ws_a={}&ws_m={}'.format(random_year, ws_a, ws_m)
        print(request_url)
        if(stockcode.replace('.MY', '').isnumeric()):
            logging.warn("Current stockcode: " + stockcode.replace('.MY', ''))
            yield scrapy.Request(
                request_url,
                callback=self.parse_historical_data,
                meta= {'stockcode': stockcode})
            

    def parse_historical_data(self,response):
        historicalData = HistoricalDataItem()
        try:
            historicalData['data'] = json.loads(response.body)['historical_data']['data']
            historicalData['stockcode'] = response.request.meta['stockcode']
            historicalData['source'] = 'bursa_malaysia'
            try:
                yield historicalData
            except Exception as e:
                logging.error("Failed in Pipeline.")
        except KeyError as e:
            stockcode = response.request.meta['stockcode']
            logging.error("Data not found (stockcode):" + stockcode)
            newstockcode = '0' + stockcode
            if('00' in stockcode):
                raise Exception('Failed second trial: ' + stockcode)
            else:
                request_url = self.bursa_malaysia_url.format(newstockcode.replace('.MY',''))
                logging.warn("New URL: " + request_url)
                yield scrapy.Request(
                    request_url,
                    callback=self.parse)