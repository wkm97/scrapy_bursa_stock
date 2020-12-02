import json

def historicalDataItemToInfluxJson(item):
    if(item['source'] == 'bursa_malaysia'):
        return bursaMalaysiaToInfluxJson(item)

# OLD VERSION
def bursaMalaysiaToInfluxJson(item):
    code = item['bursacode']

    measurement = "klse_daily"
    json_influxdb = []
    
    for record in item['data']:
        json_record = {
            "measurement" : measurement,
            "tags": {"bursacode": code},
            "time": record['date'],
            "fields":{
                "open": float(record['open']),
                "close":float(record['close']),
                "high":float(record['high']),
                "low":float(record['low']),
                "volume": int(record['vol'] if record['vol'] != '-' else 0)
            }
        }
        json_influxdb.append(json_record)
    return json_influxdb
    

# OLD VERSION
# def bursaMalaysiaToInfluxJson(item):
#     with open('./data/tickers_final.json') as json_file:
#         tickers_map = json.load(json_file)

#     stockcode = item['stockcode']
#     # TODO fix leading 0 stockcode

#     code = stockcode.replace('.MY', '')

#     try:
#         ticker = [ticker for ticker in tickers_map if ticker['bursacode'] == code][0]
#         tags = {
#                 "stockcode":  ticker['bursacode'],
#                 "name": ticker['name'],
#                 "reuters": ticker['reuters'],
#                 "alias": ticker['alias'],
#                 "cashtag": ticker['stockcode'],
#                 "economicsector":ticker['economicsectorcode'],
#                 "industrygroup":ticker['industrygroupcode']
#             }
#     except IndexError as e:
#         tags = {"stockcode": code}

#     measurement = "klse_daily"
#     json_influxdb = []
    
#     for record in item['data']:
#         json_record = {
#             "measurement" : measurement,
#             "tags": tags,
#             "time": record['date'],
#             "fields":{
#                 "open": float(record['open']),
#                 "close":float(record['close']),
#                 "high":float(record['high']),
#                 "low":float(record['low']),
#                 "volume": int(record['vol'] if record['vol'] != '-' else 0)
#             }
#         }
#         json_influxdb.append(json_record)
#     return json_influxdb
