import re
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

    first_result = req_index.json()["hits"]["hits"][0]
    if first_result['_source']['tickers'] == ticker:

        cik_without_0 = first_result['_id']
        cik = '0'*(10-len(cik_without_0))+cik_without_0

    return cik



def date_validation(date):

    date_l = date.split('-')
    dict_months = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'} 
    date_valid = dict_months[int(date_l[1])]+f'.*{date_l[2]}.*{date_l[0]}'
    return {'regrex_expression':date_valid,'filling_year':date_l[0]}


def get_10_k_links(ticker):

    cik = search_cik(ticker)

    payload = json.dumps({"entityName":cik,"filter_forms":"10-K","startdt":"2016-12-02","enddt":"2022-12-02"})

    req = requests.post(sec_search_endpoint,headers=header_req,data=payload)

    list_fillings = req.json()['hits']['hits']

    list_adsh = [{'date':date_validation(filling['_source']['period_ending']),'url':f'https://www.sec.gov/Archives/edgar/data/{cik}/'+filling['_source']['adsh'].replace('-','')} for filling in list_fillings if filling['_source']['file_type'] == '10-K' ]

    return list_adsh



years_list = []

filling_dict = {None:{}}

def parse_statement(non_balance,file_url,date,year_filling):

    req = requests.get(file_url,headers=header_req).text

    content = BeautifulSoup(req,features="html.parser")
    rows_list = content.find('table',{"class": "report"}).find_all('tr')

    if non_balance:

        years = rows_list[1].find_all('th',attrs={'class':'th'})

        for index,year in  enumerate(reversed(years)):
            if re.search(f'{date}',year.text,re.I):
                filling_year = len(years)-(index+1)

                valid_years = [int(year_filling)-year_column for year_column in range(0,len(years[filling_year:]))]
                break

        concept_title = None

        for row in rows_list[2:]:
            
            cells = row.find_all('td',attrs={'class':re.compile('nump|num',re.I)})[filling_year:]

            if cells:
                concept = row.find('td',attrs={'class':'pl'}).getText()

                if concept in filling_dict[concept_title]:
                    pass
                else:
                    filling_dict[concept_title][concept] = {}

                for index,cell in enumerate(cells):

                    year_key = valid_years[index]
                    
                    if year_key in years_list:
                        continue

                    else:
                        if year_key in filling_dict[concept_title][concept]:
                            continue
                        else:

                            cell_class = cell.get('class')[0]
                            non_digit_filter = re.sub('\W','',cell.getText())

                            if cell_class == 'num':
                                non_digit_filter = f'({non_digit_filter})'

                            filling_dict[concept_title][concept][year_key] = non_digit_filter

            else:
                concept_title = row.find('td',attrs={'class':'pl'}).getText()

                if concept_title in filling_dict:
                    pass
                else:
                    filling_dict[concept_title] = {}
        
        else:
            for year in valid_years:
                if year in years_list:
                    continue
                else:
                    years_list.append(year)



def get_statements(event,context):

    fillings = get_10_k_links(event['ticker'])

    for filling_dict in fillings:

        filling = filling_dict['url']
        filling_date = filling_dict['date']['regrex_expression']
        filling_year = filling_dict['date']['filling_year']
       
        #time.sleep(1)
        filling_summary = filling+'/FilingSummary.xml'

        req = requests.get(filling_summary,headers=header_req)

        reports = BeautifulSoup(req.text,features='xml').find_all('Report')[1:10]
        income_state = False
        balance_state = False
        flow_state = False

        for report in reports:
            report_name = report.find('ShortName').getText().upper()
            html_file_name = report.find('HtmlFileName').getText()
            file_url = filling+f'/{html_file_name}'

            if "OPERATION" in report_name or "INCOME" in report_name or "EARNING" in report_name:
                if not income_state:
                    parse_statement(True,file_url,filling_date,filling_year)
                    income_state = True

            if "BALANCE" in report_name and "SHEET" in report_name:
                if not balance_state:
                    parse_statement(False,file_url,filling_date,filling_year)
                    balance_state = True

            if "CASH FLOW" in report_name:
                if not flow_state:
                    parse_statement(True,file_url,filling_date,filling_year)
                    flow_state = True





        






