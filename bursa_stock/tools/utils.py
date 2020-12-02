import requests

def testing():
    return ['http://quotes.toscrape.com']

def getListOfSymbols():
    default_url = "http://www.bursamarketplace.com/index.php?tpl=stock_ajax&type=listing&pagenum={}&sfield=name&stype=asc&midcap=0"
    all_records = []
    page = 1
    while True:
        try:
            response = requests.get(default_url.format(page), timeout=(1, 3))
            current_records = response.json()
            all_records = all_records + current_records['records']
            page = current_records['nextpage']
            if(page > current_records['totalpage']):
                print(page)
                break

        except Exception as e:
            print(e)
            break
    return all_records