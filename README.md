Need modify scrapy codebase to enable request parameter.
Reference: https://github.com/scrapinghub/scrapyrt/issues/29

cd to working directory
scrapyrt -p 8080

# REQUEST

curl --location --request POST 'http://localhost:8080/crawl.json' \
--header 'Content-Type: application/json' \
--data-raw '{ "start_requests":true, "bursacode":"7247", "spider_name": "bursa_malaysia_ticker_data"}'
