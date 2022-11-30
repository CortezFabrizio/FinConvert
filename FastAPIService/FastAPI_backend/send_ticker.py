from fastapi import FastAPI
import json
import boto3
from pydantic import BaseModel

app = FastAPI()


class Ticker(BaseModel):
    name: str


@app.get("/get-ticker")
def read_root(ticker:str):

    parameter = {'ticker':ticker}

    client = boto3.client('lambda')

    response = client.invoke(FunctionName='ticker_process',Payload=json.dumps(parameter))

    parsed_response = response['Payload']

    json_res = json.loads(parsed_response.read().decode("utf-8"))

     
    return json_res
