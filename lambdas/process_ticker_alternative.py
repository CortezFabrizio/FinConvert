import requests
import json
import time
from bs4 import BeautifulSoup

sec_search_endpoint = 'https://efts.sec.gov/LATEST/search-index'

header_req = {
"user-Agent":"fabriziocortez17@gmail.com",
"accept-Encoding":"gzip, deflate, br",
"origin":"https://www.sec.gov",
"content-type":"application/x-www-form-urlencoded; charset=UTF-8",
"cache-control": "no-cache",
"referer":"https://www.sec.gov/"
}


def search_cik(ticker):
    print(ticker)

    payload_d = json.dumps({"keysTyped":ticker})

    req_index = requests.post(url=sec_search_endpoint,data=payload_d,headers=header_req)

    cik = req_index.json()["hits"]["hits"][0]["_id"]

    return cik


def get_10_k_links(ticker):

    cik = search_cik(ticker)

    payload = json.dumps({"entityName":ticker,"filter_forms":"10-K","startdt":"2017-12-02","enddt":"2022-12-02"})

    req = requests.post(sec_search_endpoint,headers=header_req,data=payload)

    list_fillings = req.json()['hits']['hits']

    list_adsh = [f'https://www.sec.gov/Archives/edgar/data/{cik}/'+filling['_source']['adsh'].replace('-','') for filling in list_fillings]

    return list_adsh



def get_statements(event,context):

    fillings = get_10_k_links(event['ticker'])

    statements = {'income':[],'balance':[],'flows':[]}

    for filling in fillings:

        time.sleep(1)

        for index in range(2,7):

            time.sleep(1)

            b = filling+f'/R{str(index)}.htm'

            req = requests.get(b,headers=header_req).text

            rows_list = BeautifulSoup(req,features="html.parser").find('table',{"class": "report"}).find_all('tr')

            title = rows_list[0].find('th').getText().upper()
            
            if "OPERATION" in title or "INCOME" in title or "EARNING" in title:

                statements['income'].append(filling)
                continue

            if "BALANCE" in title and "SHEET" in title:
                statements['balance'].append(filling)

                continue

            if "CASH FLOW" in title:
                statements['flows'].append(filling)

                continue







