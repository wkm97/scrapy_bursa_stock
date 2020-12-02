import scrapy
import json
from ..items import TickerInfoItem
from pymongo import MongoClient
import sys

try:
    client = MongoClient("mongodb+srv://wkm97:1504750@klse-s6tb2.mongodb.net/test?retryWrites=true&w=majority")
    db = client.get_database('klse')
    # db.avoidDuplicateEntriesDemo.createIndex({"stockcode":1},{unique:true})
except Exception as e:
    print(repr(e))
    sys.exit(1)

class KlseTickersSpider(scrapy.Spider):
    name = 'klse_tickers_list'
    default_url = "http://www.bursamarketplace.com/index.php?tpl=stock_ajax&type=listing&pagenum={}&sfield=name&stype=asc&midcap=0"
    custom_settings = {
        'ITEM_PIPELINES': {
            'bursa_stock.pipelines.BursaStockPipeline': 300,
        }
    }

    def start_requests(self):
        yield scrapy.Request(
            self.default_url.format(1),
            meta={'page_number': 1},
            headers={'accept': 'application/json'}
        )
            

    def parse(self, response):
        bursamarket_url = "http://www.bursamarketplace.com/index.php?tpl=stock_ajax&type=gettixdetail&code={}"
        json_result = json.loads(response.body)
        total_page, next_page = json_result['totalpage'], json_result['nextpage']
        for record in json_result['records']:
            stockcode = record['stockcode'] #Used by reuters
            name = record['name']
            cashtag = record['cashtag'] #Used by bursa market
            yield scrapy.Request(
                bursamarket_url.format(cashtag.replace('$', '')),
                meta={'stockcode': stockcode, 'name':name, 'cashtag':cashtag},
                callback=self.parse_enrich)
            # yield {"stockcode":stockcode, "name":name, "cashtag":cashtag}
        
        if next_page <= total_page:
            yield scrapy.Request(
                self.default_url.format(next_page),
                meta={'page_number': next_page},
            )
    
    def parse_enrich(self, response):
        records = db.ticker_records
        tickerInfo = TickerInfoItem()
        required_cols = ["stockcode", "bursacode", "bloomberg", "alias", "name", "reuters", "economicsectorcode", "industrygroupcode", "businesssummary"]
        json_result = json.loads(response.body)
        json_result = { col_name : json_result[col_name] for col_name in required_cols}
        records.update({'stockcode': json_result['stockcode']}, json_result, upsert=True)
        tickerInfo['stockcode'] = json_result['stockcode']
        tickerInfo['bursacode'] = json_result['bursacode']
        tickerInfo['bloomberg'] = json_result['bloomberg']
        tickerInfo['alias'] = json_result['alias']
        tickerInfo['name'] = json_result['name']
        tickerInfo['reuters'] = json_result['reuters']
        tickerInfo['economicsectorcode'] = json_result['economicsectorcode']
        tickerInfo['industrygroupcode'] = json_result['industrygroupcode']
        tickerInfo['businesssummary'] = json_result['businesssummary']
        print(json_result)
        yield json_result



class EnrichKlseTickersInfo(scrapy.Spider):
    name = 'klse_tickers_enrich'
    custom_settings = {
        'ITEM_PIPELINES': {
            'bursa_malaysia.pipelines.BursaStockPipeline': 300,
        }
    }
    bursamarket_url = "http://www.bursamarketplace.com/index.php?tpl=stock_ajax&type=gettixdetail&code={}"
    required_cols = ["stockcode", "bursacode", "bloomberg", "alias", "name", "reuters", "economicsectorcode", "industrygroupcode", "businesssummary"]
    def start_requests(self):
        with open('./data/tickers_stage_1.json') as json_file:
            tickers = json.load(json_file)
        for ticker in tickers:
            yield scrapy.Request(
                self.bursamarket_url.format(ticker['cashtag'].replace('$', '')),
                )
    
    def parse(self, response):
        json_result = json.loads(response.body)
        json_result = { col_name : json_result[col_name] for col_name in self.required_cols}
        yield json_result
        
        