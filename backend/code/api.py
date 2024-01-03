#!/usr/bin/python3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import jwt, yaml
from datetime import datetime
from scipy.interpolate import lagrange
from os import environ
from secrets import token_hex
import db

SMOOTHING_CONSTANT = 5

secret = environ.get('SECRET', token_hex(20))
print(secret)
configurationFile=environ.get('CONFIGURATION_FILE', 'configuration.yaml')

api = FastAPI()

class Result(BaseModel):
    token: str
    results: list[str]
    
results:dict[str, list[list[str]]] = {}

@api.post('/register_device/')
def add_device(location:str='', silent=False, correlationCoefficients:list[float]=[0.0, 1.0]):
    if not location in results:
        results.update({location: [[]]})
        if not db.addLocation(location, correlationCoefficients):
            raise HTTPException(500, 'Internal Server Error')
    else:
        results[location].append([])
    payload = {'deviceID':len(results[location])-1, 'location':location}
    token = jwt.encode(payload, key=secret)
    if not silent:
        print(f'generated token with payload: {payload}')
    return {'token':token}

@api.post('/adjust_coeficients/')
def adjust_coeficients(location:str, timestamps:list[float], desiredResults:list[float]):
    actualResults = [db.getDataByTimestamp(location, timestamp)[0] for timestamp in timestamps]
    if None in actualResults:
        raise HTTPException(404, f'Timestamp {actualResults.index(None)} has no been found in the database')
    coefficients = lagrange(actualResults, desiredResults).coefficients
    db.chageCoefficients(location, list(coefficients))

@api.post('/submit_result/')
def submit_result(result:Result):
    payload = jwt.decode(result.token, secret, algorithms=['HS256', ])
    location = payload['location']
    deviceNumber = int(payload['deviceID'])
    if not location in results or not len(results[location])>=deviceNumber:
        raise HTTPException(status_code=404, detail='The specified device was not found')
    results[location][deviceNumber] = result.results
    print(f'device at {location} reported {len(result.results)} devices')
    if deviceNumber == 0:
        calculateResult(location)
    return ''

@api.get('/list_devices/')
def list_devices():
    print(results)
    return list(results.keys())

@api.post('/get_location_info/')
def get_location_info(location:str, count:int=5):
    if not location in results:
        raise HTTPException(status_code=404, detail='The specified device was not found')
    result = db.getData(location, count+SMOOTHING_CONSTANT)
    correlationCoefficients = db.getLocation(location)['correlationCoefficients']
    return [correlationFunction(resultsFilter(result[i:i+SMOOTHING_CONSTANT]), correlationCoefficients) for i in range(count)]

def correlationFunction(value:float, coefficients:list[float]=None) -> float:
    return sum([coefficient * value**i for i, coefficient in enumerate(coefficients)])

def resultsFilter(data:list[int], filterConstant:float=0.2):
    if not len(data):
        return 0
    filterValue = data[0]
    for d in data[1:]:
        filterValue = (1-filterConstant)*filterValue + filterConstant * d
    return filterValue

def calculateResult(location:str):
    processedResult = set(results[location][0])
    for s in results[location][1:]:
        if not len(s):
            continue
        processedResult = processedResult.intersection(set(s))
    if not db.addData(location, len(processedResult)):
        raise HTTPException(500, 'Internal Server Error')

@api.get('/configure/')
def configure():
    if not configurationFile is None:
        with open(configurationFile) as f:
            configuration = yaml.safe_load(f)
            return {f'{id}{i}':add_device(id, silent=True, correlationCoefficients=[0.0, 1.0])["token"] for id, location in configuration['locations'].items() for i in range(location['endpoints'])}
#    uvicorn.run(api, host='0.0.0.0')