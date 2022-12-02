import requests
import json
import bs4

header_req = {"User-Agent":"fabriziocortez17@icloud.com","Accept-Encoding":"gzip,deflate","Host":"www.sec.gov"}

def search_cik(ticker):
    print(ticker)

    url_index = 'https://efts.sec.gov/LATEST/search-index'

    payload = {"keysTyped":ticker}

    req_index = requests.post(url=url_index,data=json.dumps(payload),headers=header_req)

    cik = req_index.json()["hits"]["hits"][0]["_id"]
    return cik


def get_10_k_links(ticker):

    cik = search_cik(ticker)
    
    url_search = f'https://www.sec.gov/edgar/search/#/entityName={cik}&filter_forms=10-K'

    req = requests.get(url_search).text


    parse_fillings = bs4.BeautifulSoup(req,features="html.parser").findAll("a",{"class":"preview-file"})

    fillings_id = [f'https://www.sec.gov/Archives/edgar/data/{cik}/'+link['data-adsh'] for link in parse_fillings ]

    return fillings_id


def get_fillings(event,context):

    paths = get_10_k_links(event['ticker'])

    for link in paths:

        requests.get(link+'/R2.htm')




