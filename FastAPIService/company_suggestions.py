import json
import requests
import os


header_req_index = {
    "user-Agent":os.getenv('USER_AGENT'),
    "accept-Encoding":"gzip, deflate, br",
    "origin":"https://www.sec.gov",
    "cache-control": "no-cache",
    "referer":"https://www.sec.gov/",
    "accept": "application/json, text/javascript, */*; q=0.01",
    "pragma":"no-cache"
    }

def company_searcher (Typed,response):

    response.headers['Access-Control-Allow-Origin'] = '*'

    keys_typed = Typed.strip(' ').upper()

    req_search = requests.get(f'https://efts.sec.gov/LATEST/search-index?keysTyped={keys_typed}',headers=header_req_index)

    if req_search.status_code == 200 :
        results = req_search.json()['hits']['hits']
        list_results = [{'ticker':result['_source']['tickers'].split(',')[0],'name':result['_source']['entity']} for result in results if 'tickers' in result['_source']]

        if list_results:
            return json.dumps(list_results)
        else:
            return json.dumps([{'error':'No tickers found'}])
    
    else:

        return json.dumps([{'error':'SEC endpoint could not process the request'}])
