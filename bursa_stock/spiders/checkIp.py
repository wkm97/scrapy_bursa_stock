import scrapy

class CheckIp(scrapy.Spider):
    name = "checkip"
    custom_settings = {
        'ITEM_PIPELINES': {
            'bursa_malaysia.pipelines.BursaStockPipeline': 300,
        }
    }
    start_urls = ("http://icanhazip.com/",)
    # start_urls = ("https://botproxy.net/docs/how-to/how-to-solve-403-error-in-scrapy/",)

    def parse(self, resp):


        request_headers = resp.request.headers
        ua = request_headers.get("User-Agent")
        ip = resp.text.strip()

        yield {'IP_ADDRESS': ip}