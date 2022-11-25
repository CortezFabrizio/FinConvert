FROM python:3.11

SHELL ["/bin/bash", "-c"]

WORKDIR /fastAPI

COPY ./FastAPI_backend /fastAPI/


RUN pip install uvicorn
RUN pip install fastapi

CMD ["uvicorn", "test:app", "--host", "0.0.0.0", "--port", "80"]
