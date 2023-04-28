FROM python:3.11

SHELL ["/bin/bash", "-c"]

WORKDIR /fastAPI

COPY ./get_financials.py /fastAPI/
COPY ./exception_handler_functions.py /fastAPI/

RUN pip install uvicorn
RUN pip install fastapi
RUN pip install requests
RUN pip install boto3
RUN pip install openpyxl
RUN pip install beautifulsoup4
RUN pip install lxml

#RUN apt-get update && \
#    apt-get -y install nginx

#COPY ./nginx/nginx.conf /etc/nginx/conf.d

#RUN rm /etc/nginx/sites-enabled/default
#RUN rm /etc/nginx/sites-available/default

EXPOSE 8000

CMD ["/bin/sh","-c","uvicorn get_financials:app --host 0.0.0.0 --port 8000"]

