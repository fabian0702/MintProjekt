#from flask import Flask, request, Blueprint, abort
from fastapi import FastAPI, HTTPException, Body
import jwt, uvicorn
from typing import Annotated

secret = 'abcdef'
api = FastAPI()

results:dict[str, list[list[str]]] = {}
pastResults:dict[str, list[str]] = {}

@api.post('/api/register_device/')
def add_device(location:str=''):
    if not location in results:
        results.update({location: [[]]})
        pastResults.update({location:[]})
    else:
        results[location].append([])
    payload = {'device':len(results[location])-1, 'device_location':location}
    token = jwt.encode(payload, key=secret)
    print(f'generated token with payload: {payload}')
    return {'token':token}

@api.post('/api/submit_result/')
def submit_result(result:Annotated[int, Body(embed=True)], token:Annotated[str, Body(embed=True)]):
    payload = jwt.decode(token, secret, algorithms=['HS256', ])
    location = payload['device_location']
    deviceNumber = int(payload['device'])
    if not location in results or not len(results[location])>=deviceNumber:
        raise HTTPException(status_code=404, detail='The specified device was not found')
    results[location][deviceNumber] = result
    print(f'device at {location} reported {len(result)} devices')
    if deviceNumber == 0:
        print(results, filteredResults())
    return ''

@api.get('/api/list_devices/')
def list_devices():
    print(results)
    return list(results.keys())

@api.post('/api/get_location_info/')
def get_location_info(location:str):
    if not location in results:
        raise HTTPException(status_code=404, detail='The specified device was not found')
    return filteredResults()[location]

def resultsFilter(data:list[int], filterConstant:float=0.2):
    if not len(data):
        return 0
    filterValue = data[0]
    for d in data[1:]:
        filterValue = (1-filterConstant)*filterValue + filterConstant * d
    return filterValue



def filteredResults():
    for location in results:
        processedResult = set(results[location][0])
        for s in results[location][1:]:
            processedResult = processedResult.intersection(set(s))
        pastResults[location].append(len(processedResult))
    
    return {x:resultsFilter() for x in pastResults}

if __name__ == '__main__':
    uvicorn.run(api)