FROM python:3.11

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt 
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt
 
COPY ./api.py /code/api.py
COPY ./log.conf /code/log.conf

CMD ["uvicorn", "api:api", "--host", "0.0.0.0", "--port", "8000", "--log-config", "log.conf"]