#!/usr/bin/python3
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import jwt, yaml
from datetime import datetime
from scipy.interpolate import lagrange
from os import environ
from secrets import token_hex
import db

SECRET = environ.get('SECRET', token_hex(20))
CONFIGURATION_FILE=environ.get('CONFIGURATION_FILE', 'configuration.yaml')
    
results:dict[str, dict[int, list[str]]] = {}

def add_device(location:str='', id=None, correlationCoefficients:list[float]=[0.0, 1.0]):
    id = len(results.get(location, [])) if id is None else id
    if not location in results:
        results.update({location: {0: []}})
        if not db.addLocation(location, correlationCoefficients):
            raise HTTPException(500, 'Internal Server Error')
    elif len(results[location]) <= id:
        results[location].update({id:[]})
    
    payload = {'id':id, 'location':location}
    token = jwt.encode(payload, key=SECRET)
    print({f'{location}{payload["id"]}':token})

    return {'id':f'{location}{payload["id"]}','token':token}

with open(CONFIGURATION_FILE) as f:
    configuration = yaml.safe_load(f)

    for name, location in configuration['locations'].items():
        for id in range(location['endpoints']):
            add_device(name, id, correlationCoefficients=location['mappingcoeficients'])
    
    SMOOTHING_CONSTANT = configuration.get('smoothing_constant', 0.2)
    SMOOTHING_NUMBER = configuration.get('smoothing_constant', 5)

api = FastAPI()

class Result(BaseModel):
    token: str
    results: list[str]

@api.post('/register_device/')
def register_device(location:str='', correlationCoefficients:list[float]=[0.0, 1.0]):
    return add_device(location, None, correlationCoefficients)

@api.get('/list_devices/')
def list_devices():
    tokens = {}
    for location in results:
        print(location, results[location])
        for id in results[location]:
            payload = {'id':id, 'location':location}
            tokens.update({f'{location}{id}':{'token':jwt.encode(payload, key=SECRET), 'location':location, 'id':id}})
    return tokens

@api.get('/get_locations/')
def list_devices():
    tokens = []
    for location in results:
        tokens.append(location)
    return tokens

@api.post('/remove_device/')
def remove_device(token:str):
    payload = jwt.decode(token, key=SECRET, algorithms=['HS256', ])
    location = payload['location']
    deviceNumber = int(payload['id'])
    if not location in results or not len(results[location])>=deviceNumber:
        raise HTTPException(status_code=404, detail='The specified device was not found')
    results[location].pop(deviceNumber)
    if not len(results[location]):
        return db.removeLocation(location), results.pop(location)

@api.post('/adjust_coeficients/')
def adjust_coeficients(location:str, timestamps:list[float], desiredResults:list[float]):
    actualResults = [db.getDataByTimestamp(location, timestamp)[0] for timestamp in timestamps]
    if None in actualResults:
        raise HTTPException(404, f'Timestamp {actualResults.index(None)} has no been found in the database')
    coefficients = lagrange(actualResults, desiredResults).coefficients
    return db.chageCoefficients(location, list(coefficients))

@api.post('/submit_result/')
def submit_result(result:Result):
    payload = jwt.decode(result.token, SECRET, algorithms=['HS256', ])
    location = payload['location']
    deviceNumber = int(payload['deviceID'])
    if not location in results or not len(results[location])>=deviceNumber:
        raise HTTPException(status_code=404, detail='The specified device was not found')
    results[location][deviceNumber] = result.results
    print(f'device at {location} reported {len(result.results)} devices')
    if deviceNumber == 0:
        calculateResult(location)

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
    return [correlationFunction(resultsFilter(result[i:i+SMOOTHING_NUMBER]), correlationCoefficients) for i in range(count)]

def correlationFunction(value:float, coefficients:list[float]=None) -> float:
    return sum([coefficient * value**i for i, coefficient in enumerate(coefficients)])

def resultsFilter(data:list[int]):
    if not len(data):
        return 0
    filterValue = data[0]
    for d in data[1:]:
        filterValue = (1-SMOOTHING_CONSTANT)*filterValue + SMOOTHING_CONSTANT * d
    return filterValue

def calculateResult(location:str):
    processedResult = set(results[location][0])
    for s in results[location][1:]:
        if not len(s):
            continue
        processedResult = processedResult.intersection(set(s))
    if not db.addData(location, len(processedResult)):
        raise HTTPException(500, 'Internal Server Error')