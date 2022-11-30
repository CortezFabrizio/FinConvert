import io

import bs4
import json
import requests
import openpyxl

hed = {"User-Agent":"fabriziocortez17@gmail.com","Accept-Encoding":"gzip,deflate","Host":"www.sec.gov"}

##ADT
def CIK_finder(tik):
    ticker = tik
    sec_search_index = "https://efts.sec.gov/LATEST/search-index"
    header = {"keysTyped":ticker}

    req = requests.post(sec_search_index,data = json.dumps(header))

    cik = req.json()["hits"]["hits"][0]["_id"]
    return cik




def Get_company_fillings(tick):
    url = "https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK="+CIK_finder(tick)+"&type=10-K&dateb=&owner=exclude&count=40&search_text="
    reqq = requests.get(url,headers = hed)
    mm = bs4.BeautifulSoup(reqq.text,features="html.parser").findAll("a",attrs={"id":"interactiveDataBtn"})

    valid_ones = []

    for elem in mm:
        row_parent = bs4.BeautifulSoup.find_previous_sibling(elem.parent)
        row_parent_text = row_parent.string

        if row_parent_text == "10-K":
            valid_ones.append(elem)

    return valid_ones




def Section_Parser(urll):
    req = requests.get(urll).text
    kll = bs4.BeautifulSoup(req,features="html.parser").findAll("a",{"href":"#"})[0:6]

    for elem in kll:
        if elem.string == "Financial Statements":
            list_financials_sec = bs4.BeautifulSoup.find_next_sibling(elem)
            oppp= list_financials_sec.findAll("li")

            income_state = False
            balance_state = False
            cash_flows_state = False

            for elem_l in oppp:

                title = elem_l.string.upper()
                if "OPERATION" in title or "INCOME" in title or "EARNING" in title:
                    if income_state == False:
                        index = int(elem_l["id"][1])
                        print(index)
                        income_state = True


                if "BALANCE" in title and "SHEET" in title:
                    if balance_state == False:
                        indexp = int(elem_l["id"][1])
                        print(indexp)
                        balance_state = True

                if "CASH FLOW" in title:
                    if cash_flows_state == False:
                        index3 = int(elem_l["id"][1])
                        cash_flows_state = True



            libe = {"Income State":index-1,"Balance Sheet":indexp-1,"Cash Flows":index3-1}
            print(libe)
            return libe


def Get_excels_urls(sec_url):
    o = requests.get(sec_url).text
    excel_finder = bs4.BeautifulSoup(o,features="html.parser").findAll("a",class_="xbrlviewer")


    return excel_finder[1]["href"]




header = {"User-Agent":"fabriziocortez17@gmail.com","Accept-Encoding":"gzip,deflate","Host":"www.sec.gov"}



def Section_finder (event,context):
    
    values_list = []

    values_dict = {"Values":values_list}
    
    timer = 1

    for elem in Get_company_fillings(event["ticker"]):

        
        
        sec_urll = "https://www.sec.gov/"+elem["href"]

        ss = Section_Parser(sec_urll)

        url2 ="https://www.sec.gov"+Get_excels_urls(sec_urll)
        req2 = requests.get(url2, headers=header).content


        sha = openpyxl.load_workbook(io.BytesIO(req2),read_only=True).worksheets[ss["Income State"]].values.__iter__()


        for el in ss.keys():
            sheet = openpyxl.load_workbook(io.BytesIO(req2),read_only=True).worksheets[ss[el]].values
            
            
            for valor in sheet:
                values_list.append(valor)
                
        timer = timer+1
        if timer == 5:
            return values_dict
                
            print("---------------------------------------------------------")

        print("---------------------------------------------------------------------------------------------------------------")