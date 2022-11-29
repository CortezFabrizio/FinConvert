from fastapi import FastAPI
import requests
import json
import os
import boto3
from pydantic import BaseModel

app = FastAPI()


class Ticker(BaseModel):
    name: str


@app.get("/get-ticker")
def read_root(ticker:str):

    sqs = boto3.resource('sqs')

    print(ticker)
    queue = sqs.get_queue_by_name(QueueName='TickerQueue')

    response = queue.send_message(MessageBody=ticker)


    return {"Hello": ticker}
