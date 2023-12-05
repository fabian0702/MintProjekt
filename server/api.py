#from flask import Flask, request, Blueprint, abort
from fastapi import FastAPI, HTTPException, Body
import jwt, uvicorn
from typing import Annotated

secret = 'abcdef'
api = FastAPI()

results:dict[str, list[int]] = {}

@api.post('/register_device/')
def add_device(location:str=''):
    results.update({location: []})
    payload = {'device':len(results), 'device_location':location}
    token = jwt.encode(payload, key=secret)
    print(f'generated token with payload: {payload}')
    return {'token':token}

@api.post('/submit_result/')
def submit_result(result:Annotated[int, Body(embed=True)], token:Annotated[str, Body(embed=True)]):
    payload = jwt.decode(token, secret, algorithms=['HS256', ])
    location = payload['device_location']
    if not location in results:
        raise HTTPException(status_code=404, detail='The specified device was not found')
    results[location].append(int(result))
    print(f'device at {location} reported {result} devices')
    print(results, filteredResults())
    return ''

def resultsFilter(data:list[int], filterConstant:float=0.2):
    if not len(data):
        return 0
    filterValue = data[0]
    for d in data[1:]:
        filterValue = (1-filterConstant)*filterValue + filterConstant * d
    return filterValue

def filteredResults():
    return {x:resultsFilter(results[x]) for x in results}

if __name__ == '__main__':
    uvicorn.run(api)