# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from .items import HistoricalDataItem
from influxdb import InfluxDBClient
import influxdb
from .tools.processHistoricalData import historicalDataItemToInfluxJson
import scrapy
import logging


class BursaHistoricalDataPipeline:
    def __init__(self, host, user, password, port=8086):
        self.dbname = 'historical_data'
        self.client = InfluxDBClient(host, port, user, password, self.dbname)
        self.client.create_database(self.dbname)
        self.client.switch_database(self.dbname)

    def process_item(self, item, spider):
        if isinstance(item, HistoricalDataItem):
            json_body = historicalDataItemToInfluxJson(item)
            try:
                self.client.write_points(json_body, time_precision='ms')
            except influxdb.exceptions.InfluxDBServerError as e:
                logging.error("Item Failed to Write to Influxdb (Stockcode): " + str(item['stockcode']))
            return item
        return item
    

    def spider_closed(self):
        self.client.close()

    @classmethod
    def from_crawler(cls, crawler):
        db_settings = crawler.settings.getdict("INFLUXDB_SETTINGS")
        if not db_settings: # if we don't define db config in settings
            raise NotConfigured # then reaise error
        host = db_settings['host']
        port = db_settings['port']
        user = db_settings['user']
        password = db_settings['password']
        return cls(host, user, password, port=port)


# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


class BursaStockPipeline:
    def process_item(self, item, spider):
        return item
