from flask import Flask, request, Blueprint, abort
import jwt

secret = 'abcdef'
api = Blueprint('api', __name__,)

results:dict[str, list[list[str]]] = {}
pastResults:dict[str, list[str]] = {}

@api.post('/register_device/')
def add_device():
    location = request.json['location']
    if not location in results:
        results.update({location: [[]]})
        pastResults.update({location:[]})
    else:
        results[location].append([])
    payload = {'device':len(results[location])-1, 'device_location':location}
    token = jwt.encode(payload, key=secret)
    print(f'generated token with payload: {payload}')
    return {'token':token}

@api.post('/submit_result/')
def submit_result():
    result = request.json['result']
    payload = jwt.decode(request.json['token'], secret, algorithms=['HS256', ])
    location = payload['device_location']
    deviceNumber = int(payload['device'])
    if not location in results or not len(results[location])>=deviceNumber:
        abort(404, 'The specified device was not found')
    results[location][deviceNumber] = result
    print(f'device at {location} reported {len(result)} devices')
    if deviceNumber == 0:
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
    for location in results:
        processedResult = set(results[location][0])
        for s in results[location][1:]:
            processedResult = processedResult.intersection(set(s))
        pastResults[location].append(len(processedResult))
    
    return {x:resultsFilter() for x in pastResults}