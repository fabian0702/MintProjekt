FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
 
COPY ./code/ /code/
COPY ./configuration.yaml /code/

CMD ["uvicorn", "api:api", "--host", "0.0.0.0", "--port", "8000", "--log-config", "log.conf", "--root-path", "/api"]