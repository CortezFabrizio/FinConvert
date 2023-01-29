from fastapi import FastAPI
import json
import boto3
from pydantic import BaseModel

import re
import requests
from bs4 import BeautifulSoup
from openpyxl import Workbook
from tempfile import NamedTemporaryFile


app = FastAPI()

@app.get("/get-ticker")
def read_root(ticker:str,start_date:int,end_date:int):

    #parameter = {'ticker':ticker}

    sec_search_endpoint = 'https://efts.sec.gov/LATEST/search-index'

    header_req = {
    "user-Agent":"fabriziocortezandres@gmail.com",
    "accept-Encoding":"gzip, deflate, br",
    "origin":"https://www.sec.gov",
    "content-type":"application/x-www-form-urlencoded; charset=UTF-8",
    "cache-control": "no-cache",
    "referer":"https://www.sec.gov/"
    }

    
    def search_cik(ticker):

            payload_d = json.dumps({"keysTyped":ticker})

            req_index = requests.post(url=sec_search_endpoint,data=payload_d,headers=header_req)
            first_result = req_index.json()["hits"]["hits"][0]
            if ticker in first_result['_source']['tickers']:

                cik_without_0 = first_result['_id']
                cik = '0'*(10-len(cik_without_0))+cik_without_0
                return cik


    def check_years(date_start,date_end):

        years_difference = date_end-date_start

        if search_cik(ticker):
            table = boto3.resource('dynamodb').Table('fabri_app')


            response_item = table.get_item(
            Key={
                'ticker':ticker
            },
            AttributesToGet=[
                'Balance','Cash','Income'
            ])
            
            if 'Item' in response_item:

                income_attr = response_item['Item']['Income']
                balance_attr = response_item['Item']['Balance']
                cash_attr = response_item['Item']['Cash']

                year_to_get = []
                year_to_check = []

                for year_difference in range(years_difference+1):
                    key_year = f'y{date_end-year_difference}'
                    if key_year not in income_attr and f'y{date_end-year_difference}' not in balance_attr and f'y{date_end-year_difference}' not in cash_attr:
                        year_to_check.append(date_end-year_difference)
                    else:
                        year_to_get.append(key_year)
                    

                return year_to_check

            else:
                table.put_item(
                    Item={
                        'ticker':ticker,
                        'Balance':{},
                        'Income':{},
                        'Cash':{}
                    }
                )
                year_to_check = [date_end-year_difference  for year_difference in range(years_difference+1)]
                return year_to_check



    def check_ite_exists():
        table = boto3.resource('dynamodb').Table('fabri_app')

        response_item = table.get_item(
        Key={
            'ticker':'dgdg'
        })



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

        return list_adsh


    #years_list = []

    #filling_dict = {}


    def parse_statement(non_balance,file_url,date,year_filling,filling_dict,end_date,is_income = False,valid_years_list=False):

        req = requests.get(file_url,headers=header_req).text

        content = BeautifulSoup(req,features="html.parser")
        rows_list = content.find('table',{"class": "report"}).find_all('tr')

        if non_balance:
            row_years_index = 1
            rows__first_index_concepts = 2
            if is_income and not rows_list[2].find_all('td',attrs={'class':re.compile('nump|num',re.I)}):
                rows__first_index_concepts = 3

        if not non_balance:
            row_years_index = 0
            rows__first_index_concepts = 1


        row_years = rows_list[row_years_index].find_all('th',attrs={'class':'th'})

        years = [year_row for year_row in row_years if re.findall("Jan.*\d{4}|Feb.*\d{4}|Mar.*\d{4}|Apr.*\d{4}|May.*\d{4}|Jun.*\d{4}|Jul.*\d{4}|Aug.*\d{4}|Sep.*\d{4}|Oct.*\d{4}|Nov.*\d{4}|Dec.*\d{4}", year_row.getText())]

        for index,year in enumerate(reversed(years)):
            if re.search(f'{date}',year.text,re.I):

                filling_year = len(years)-(index+1)

                valid_years = [ str(int(year_filling)-year_column) for year_column in range(0,len(years[filling_year:])) if not str(int(year_filling)-year_column) in filling_dict and int(year_filling)-year_column >= end_date  ]

                diff = len(years[filling_year:]) - len(valid_years)

                for year in valid_years:
                    if int(year) in valid_years_list:
                        filling_dict[year] = {}

                break


        concept_title = 'FirstBlock'
        for row in rows_list[rows__first_index_concepts:]:

            cells = row.find_all('td',attrs={'class':re.compile('nump|num',re.I)})
            len_cells = len(years)-len(cells)
            
            cells = row.find_all('td',attrs={'class':re.compile('nump|num',re.I)})[filling_year+diff-len_cells:]
            sub_concept = row.find('td',attrs={'class':'pl'})
            m = sub_concept.find('strong') if sub_concept else True
                    
            if not m and cells:

                    concept = row.find('td',attrs={'class':'pl'}).getText()    

                    for index,cell in enumerate(cells):

                        year_key = valid_years[index]
                        if int(year_key) not in valid_years_list:
                            continue

                        cell_class = cell.get('class')[0]
                        non_digit_filter = re.sub('\D','',cell.getText())

                        if cell_class == 'num':
                            non_digit_filter = f'({non_digit_filter})'

                        try:
                            filling_dict[year_key][concept_title][concept] = non_digit_filter
                        except:
                            filling_dict[year_key][concept_title] = {concept:non_digit_filter}
                    
            else:
                    try:
                        concept_title = row.find('td',attrs={'class':'pl'}).getText()
                    except:
                        continue        


    def get_statements(ticker,start_date,end_date,valid_years_list):



        statements = {'Balance':{},'Cash':{},'Income':{}}

        if not valid_years_list:
            return statements

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
                        parse_statement(True,file_url,filling_date,filling_year,statements['Income'],start_date,True,valid_years_list= valid_years_list)
                        income_state = True

                if "BALANCE" in report_name and "SHEET" in report_name:
                    if not balance_state:
                        parse_statement(False,file_url,filling_date,filling_year,statements['Balance'],start_date,valid_years_list= valid_years_list)
                        balance_state = True

                if "CASH FLOW" in report_name:
                    if not flow_state:
                        parse_statement(True,file_url,filling_date,filling_year,statements['Cash'],start_date, valid_years_list= valid_years_list)
                        flow_state = True

        return statements


    def create_excel(statements):

        wb = Workbook()
        sheet = wb.worksheets[0]

        row_index=3


        for statement in statements:

            column_index = 1
            if statement == 'Balance':
                column_index = 6
            if statement == 'Cash':
                column_index = 12

            sheet.cell(row=1,column=column_index ,value=statement)

            #len_row = len(statements[statement])

            for year in statements[statement]:
                sheet.cell(row=row_index,column=column_index+1,value=year)

                for concept_title in statements[statement][year]:

                    sheet.cell(row=row_index+1,column=column_index+1,value=concept_title)
                    concepts = statements[statement][year][concept_title]
                    row_index+=1

                    for concept in concepts:
                        value = concepts[concept]
                        sheet.cell(row=row_index+1,column=column_index+2,value=concept)
                        sheet.cell(row=row_index+1,column=column_index+3,value=value)
                        row_index+=1

                    else:
                        row_index+=2
                
                row_index+=4


            else:
                row_index = 3

        with NamedTemporaryFile() as tmp:
                wb.save(tmp.name)
                stream = tmp.read()

        s3_resource = boto3.resource('s3') 
        s3_resource.Object('fabri-app',f'{ticker}.xlsx').put(Body=stream) 



    def insert_table(resuslts):
        statements_results = resuslts

        update_expression = ''
        update_values = {}

        for statement in statements_results:

            for year in statements_results[statement]:

                sheet = json.dumps(statements_results[statement][year])

                attr_value = f':{statement}{year}'

                if update_expression:
                    update_expression += f', {statement}.y{year} = {attr_value}'
                    update_values[attr_value] = sheet

                else:
                    update_expression += f'SET {statement}.y{year} = {attr_value}'
                    update_values[attr_value] = sheet


        table = boto3.resource('dynamodb').Table('fabri_app')

        response = table.update_item(
            Key={
                'ticker': ticker
            },
            UpdateExpression=update_expression,

            ExpressionAttributeValues=
                update_values,
        )


    return json.dumps(financial_statements)
