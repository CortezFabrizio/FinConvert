from fastapi import FastAPI,Response,HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse


import json
import boto3
from pydantic import BaseModel
import time
import re
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from tempfile import NamedTemporaryFile


app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    list_errors = exc.errors()

    error_response = {}

    for desc_error in list_errors:
        parameter = desc_error['loc'][1]
        error_type = desc_error['type']

        if error_type == 'value_error.missing':
            error_response[parameter] = 'value is missing'

        elif error_type == 'type_error.integer':
            error_response[parameter] = 'value must be a integer'

        elif error_type == 'type_error.string':
            error_response[parameter] = 'value must be a string'

    return JSONResponse(error_response,status_code=400)


@app.get("/get-ticker")
def read_root(ticker:str,start_date:int,end_date:int,response:Response):

    response.headers['Access-Control-Allow-Origin'] = '*'

    file_path = None

    sec_search_endpoint = 'https://efts.sec.gov/LATEST/search-index'

    header_req = {
    "user-Agent":"fabriziocortezandres@gmail.com",
    "accept-Encoding":"gzip, deflate, br",
    "origin":"https://www.sec.gov",
    "content-type":"application/x-www-form-urlencoded; charset=UTF-8",
    "cache-control": "no-cache",
    "referer":"https://www.sec.gov/"
    }

    statements_structure = {}
    

    def search_cik(ticker):

            payload_d = json.dumps({"keysTyped":ticker})

            req_index = requests.post(url=sec_search_endpoint,data=payload_d,headers=header_req)
            try:
                first_result = req_index.json()["hits"]["hits"][0]
                if ticker in first_result['_source']['tickers']:

                    cik_without_0 = first_result['_id']
                    cik = '0'*(10-len(cik_without_0))+cik_without_0

                    return cik

                else:
                    raise HTTPException(status_code=400,detail="Provisioned ticker doesn't exist") 


             except:
                raise HTTPException(status_code=400,detail="Provisioned ticker doesn't exist") 



    def check_years(date_start,date_end):

        years_difference = date_end-date_start

        years_to_get = [str(date_end-difference) for difference in range(years_difference+1)]


        if search_cik(ticker):

            table = boto3.resource('dynamodb').Table('fabri_app')

            response_item = table.get_item(
            Key={
                'ticker':ticker
                }
            )

            if 'Item' in response_item:
                year_to_check = []

                dates_attr = response_item['Item']

                attributes = {}

                for date in dates_attr:
                    year = date.split('-')[0]
                    if year in attributes:
                        attributes[year].append(date)
                    else:
                        attributes[year] = [date]

                for year in years_to_get:

                    if year not in attributes:
                
                        year_to_check.append(year)

                    else:

                        dates = attributes[year]

                        for date in dates:

                            statements_structure2[date] = {}
                            
                            statements_structure2[date]['Income'] = json.loads( dates_attr[date]['Income'])
                            statements_structure2[date]['Balance'] = json.loads( dates_attr[date]['Balance'])
                            statements_structure2[date]['Cash'] = json.loads(dates_attr[date]['Cash'])

                return year_to_check

            else:
                table.put_item(
                    Item={'ticker':ticker}
                )

                return years_to_get


    def date_validation(date):

        date_l = date.split('-')
        dict_months = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'May',6:'Jun',7:'Jul',8:'Aug',9:'Sep',10:'Oct',11:'Nov',12:'Dec'}
        date_valid = dict_months[int(date_l[1])]+f'.*{date_l[2]}.*{date_l[0]}'
        return {'regrex_expression':date_valid,'filling_year':date_l[0]}


    def get_10_k_links(ticker,start_date,end_date):

        cik = search_cik(ticker)

        payload = json.dumps({"entityName":cik,"filter_forms":"10-K","startdt":f"{str(start_date)}-01-01","enddt":f"{str(end_date+1)}-12-31"})

        req = requests.post(sec_search_endpoint,headers=header_req,data=payload)

        list_fillings = req.json()['hits']['hits']

        list_adsh = [{'date':date_validation(filling['_source']['period_ending']),'url':f'https://www.sec.gov/Archives/edgar/data/{cik}/'+filling['_source']['adsh'].replace('-','')} for filling in list_fillings if filling['_source']['file_type'] == '10-K' and int(filling['_source']['period_ending'].split('-')[0]) <= end_date and int(filling['_source']['period_ending'].split('-')[0]) >= start_date ]

       if list_adsh:
            return list_adsh
        else:
            raise HTTPException(status_code=400,detail="Ticker doesn't represent a US companie")

            
            
    dates_statements_added = {}

    regex_date = re.compile(r"[A-Za-z][A-Za-z][A-Za-z]\. \d\d, \d\d\d\d")
    regex_year = re.compile(r"\d\d\d\d")
    regex_day = re.compile(r"\d\d,")
    regex_month = re.compile(r"[A-Za-z][A-Za-z][A-Za-z]", re.IGNORECASE)

    number_month_dict = {'jan': '01', 'feb': '02', 'mar': '03', 'apr': '04', 'may': '05', 'jun': '06',
                        'jul': '07', 'aug': '08', 'sep': '09', 'oct': '10', 'nov': '11', 'dec': '12'}


    def valid_format_date(input_date):
        date = regex_date.findall(input_date)[0]
        year = regex_year.findall(date)[0]
        day = regex_day.findall(date)[0][0:2]
        month = number_month_dict[regex_month.findall(date)[0].lower()]
        date_result = f'{year}-{month}-{day}'
        return date_result,year


   def parse_statement(type,non_balance,file_url,date,year_filling,end_date,is_income = False,valid_years_list=False):

        req = requests.get(file_url,headers=header_req).text

        content = BeautifulSoup(req,features="html.parser")
        rows_list = content.find('table',{"class": "report"}).find_all('tr')

        currency_desc = rows_list[0].find('th',attrs={'class':'tl'}).getText()

        if non_balance:
            row_years_index = 1
            rows__first_index_concepts = 2
            if is_income and not rows_list[2].find_all('td',attrs={'class':re.compile('nump|num',re.I)}):
                rows__first_index_concepts = 3

        if not non_balance:
            row_years_index = 0
            rows__first_index_concepts = 1


        row_years = rows_list[row_years_index].find_all('th',attrs={'class':'th'})

        years = [ regex_date.findall(year_row.getText())[0] for year_row in row_years if regex_date.findall(year_row.getText())]

        for index,year in enumerate(reversed(years)):
            if re.search(f'{date}',year,re.I):


                filling_year = len(years)-(index+1)

                valid_years = []
                invalid_years_index = []

                fillings_years = years[filling_year:]

                for index_year in range(0,len(fillings_years)):

                    current_date = fillings_years[index_year]

                    if current_date in dates_statements_added:
                        if type not in dates_statements_added[current_date]:
                            dates_statements_added[current_date].append(type)

                        else:
                            invalid_years_index.insert(0,index_year)
                            continue

                    else:
                        dates_statements_added[current_date] = [type]

                    date_formated = valid_format_date(current_date)
                    valid_date = date_formated[0]
                    current_year = date_formated[1]


                    if current_year not in valid_years_list or int(current_year) < end_date :
                        invalid_years_index.insert(0,index_year)
                        continue

                    valid_years.append(valid_date)
                    if valid_date in alternative_dict:
                        alternative_dict[valid_date][type] = {'title':currency_desc}
                        continue
                    else:
                        alternative_dict[valid_date] = {type:{'title':currency_desc}}

                break   

        concept_title = 'FirstBlock'
        for row in rows_list[rows__first_index_concepts:]:

            cells_total = row.find_all('td',attrs={'class':re.compile('nump|num|text',re.I)})
            len_cells = len(years)-len(cells_total)

            cells = row.find_all('td',attrs={'class':re.compile('nump|num|text',re.I)})[filling_year-len_cells:]
            
            sub_concept = row.find('td',attrs={'class':'pl'})

            m = sub_concept.find('strong') if sub_concept else True

            if not m and cells:

                    for invalid_index in invalid_years_index:
                            cells.pop(invalid_index)

                    concept = row.find('td',attrs={'class':'pl'}).getText()


                    for index,cell in enumerate(cells):
                        
                        year_key = valid_years[index]

                        cell_class = cell.get('class')[0]

                        non_digit_filter = re.sub('\D','',cell.getText())

                        if cell_class == 'num':
                            non_digit_filter = f'({non_digit_filter})'

                        try:
                            alternative_dict[year_key][type][concept_title][concept] = non_digit_filter

                        except:
                            alternative_dict[year_key][type][concept_title] = {concept: non_digit_filter}

            else:
                    try:
                        concept_title = row.find('td',attrs={'class':'pl'}).getText()
                    except:
                        continue        


    def get_statements(ticker,start_date,end_date,valid_years_list_global):

        if not valid_years_list_global:
            return False

        fillings = get_10_k_links(ticker,start_date,end_date)

        for filling_dict in fillings:
            filling = filling_dict['url']
            filling_date = filling_dict['date']['regrex_expression']
            filling_year = filling_dict['date']['filling_year']

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

                        print(file_url,alternative_dict)
                        parse_statement('Income',True,file_url,filling_date,filling_year,start_date,True,valid_years_list= valid_years_list_global)
                        income_state = True

                if "BALANCE" in report_name and "SHEET" in report_name:
                    if not balance_state:
                        print(file_url,alternative_dict)

                        parse_statement('Balance',False,file_url,filling_date,filling_year,start_date,valid_years_list= valid_years_list_global)
                        balance_state = True

                if "CASH FLOW" in report_name:
                    if not flow_state:
                        print(file_url,alternative_dict)
                        parse_statement('Cash',True,file_url,filling_date,filling_year,start_date, valid_years_list= valid_years_list_global)
                        flow_state = True

        for year in alternative_dict:
            statements_structure[year] = alternative_dict[year]

        return alternative_dict
        

  


    results = get_statements(ticker,start_date,end_date,check_years(start_date,end_date))

    if result:
        sqs = boto3.client('sqs')

        message = json.dumps(alternative_dict)

        sqs_attribute = {
                'ticker': {
                    'DataType': 'String',
                    'StringValue': ticker
                }
        }


        sqs.send_message(
            QueueUrl='https://sqs.us-west-2.amazonaws.com/847350992021/TickerQueue',
            MessageBody=message,
            MessageAttributes=sqs_attribute
        )

    return json.dumps(statements_structure)

