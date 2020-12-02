import scrapy
import json
from ..items import HistoricalDataItem
import random
import logging
import re
from ..mongoClient.client import mongoClient
from ..tools.fixBursaCode import fixBursaCode
from ..tools.processHistoricalData import historicalDataItemToInfluxJson

class BursaMalaysiaTopVolumeDataSpider(scrapy.Spider):
    name = 'bursa_top_volume'
    top_volume_url = 'https://www.bursamalaysia.com/market_information/equities_prices?keyword=&top_stock=top_active&board=&alphabetical=&sector=&sub_sector=&per_page=50&page={}'
    client = mongoClient()
    client.conn()
    db = client.db
    count = 0
    limit = 100
    custom_settings = {
        'ITEM_PIPELINES': {
            'bursa_stock.pipelines.BursaHistoricalDataPipeline': 300,
        }
    }

    
    def start_requests(self):
        page=1
        while (self.count < self.limit):
            print("COUNT : {}".format(page))
            yield scrapy.Request(
                self.top_volume_url.format(page),
                callback=self.parse
                )
            page += 1

    def parse(self, response):
        bursa_malaysia_url = 'https://www.bursamalaysia.com/trade/trading_resources/listing_directory/company-profile?stock_code={}'
        ticker_collection = self.db.ticker_records
        codes = response.xpath('//*[@id="data-1"]/td[3]')
        for code in codes:
            if(self.count == self.limit):
                break
            code = code.extract()
            code = re.search('<td>(.*)</td>', code, re.IGNORECASE).group(1)
            if(fixBursaCode(ticker_collection, code)):
                yield scrapy.Request(
                    bursa_malaysia_url.format(code),
                    callback=self.parse_token
                )
                self.count += 1
                print("COUNT: {}".format(self.count))
                print('success: {}'.format(code))
            else:
                print('fail: {}'.format(code))
    
    def parse_token(self, response):
        # /section[2]/div/div/div[2]/div/div/div
        stockcode = response.xpath("//div[@id='stockChartContainer']/@data-stock-code")[0].extract()
        api_source = response.xpath("//div[@id='stockChartContainer']/@data-api-source")[0].extract()
        ws_a = response.xpath("//div[@id='stockChartContainer']/@data-ws-a")[0].extract()
        ws_m = response.xpath("//div[@id='stockChartContainer']/@data-ws-m")[0].extract()
        random_year = 1997 #random.randint(2010, 2014)
        request_url = 'https:' + api_source + '?stock_code={}'.format(stockcode) + '&mode=historical&from_date={}0508&ws_a={}&ws_m={}'.format(random_year, ws_a, ws_m)
        
        if(stockcode.replace('.MY', '').isnumeric()):
            code = stockcode.replace('.MY', '')
            print("Current stockcode: " + code)
            # logging.warn("Current stockcode: " + stockcode.replace('.MY', ''))
            yield scrapy.Request(
                request_url,
                callback=self.parse_historical_data,
                meta= {'bursacode': code})

    def parse_historical_data(self,response):
        historicalData = HistoricalDataItem()
        try:
            historicalData['data'] = json.loads(response.body)['historical_data']['data']
            historicalData['bursacode'] = response.request.meta['bursacode']
            historicalData['source'] = 'bursa_malaysia'
            # json_body = historicalDataItemToInfluxJson(historicalData)
            yield historicalData
        except Exception as e:
            print(repr(e))

    
    def closed(self, reason):
        self.client.close()


class BursaMalaysiaHistoricalDataSpider(scrapy.Spider):
    name = 'bursa_malaysia_historical_data'
    bursa_malaysia_url = 'https://www.bursamalaysia.com/trade/trading_resources/listing_directory/company-profile?stock_code={}'
    source = 'bursa_malaysia'
    custom_settings = {
        'ITEM_PIPELINES': {
            'bursa_malaysia.pipelines.BursaHistoricalDataPipeline': 300,
        }
    }
    # start_urls = ['https://www.bursamalaysia.com/trade/trading_resources/listing_directory/company-profile?stock_code=5250']


    def start_requests(self):
        with open('./data/tickers_final.json') as json_file:
            tickers = json.load(json_file)
        for ticker in tickers[770:772]:
            yield scrapy.Request(
                self.bursa_malaysia_url.format(ticker['bursacode']),
                )
    
    def parse(self, response):
        # /section[2]/div/div/div[2]/div/div/div
        stockcode = response.xpath("//div[@id='stockChartContainer']/@data-stock-code")[0].extract()
        api_source = response.xpath("//div[@id='stockChartContainer']/@data-api-source")[0].extract()
        ws_a = response.xpath("//div[@id='stockChartContainer']/@data-ws-a")[0].extract()
        ws_m = response.xpath("//div[@id='stockChartContainer']/@data-ws-m")[0].extract()
        random_year = 1997 #random.randint(2010, 2014)
        request_url = 'https:' + api_source + '?stock_code={}'.format(stockcode) + '&mode=historical&from_date={}0428&ws_a={}&ws_m={}'.format(random_year, ws_a, ws_m)
        
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
        

