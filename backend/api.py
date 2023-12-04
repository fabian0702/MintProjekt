from flask import Flask, request, Blueprint, abort
import jwt

secret = 'abcdef'
api = Blueprint('api', __name__,)

results:dict[str, list[int]] = {}

@api.post('/register_device/')
def add_device():
    location = request.json['location']
    results.update({location: []})
    payload = {'device':len(results), 'device_location':location}
    token = jwt.encode(payload, key=secret)
    print(f'generated token with payload: {payload}')
    return {'token':token}

@api.post('/submit_result/')
def submit_result():
    result = request.json['result']
    payload = jwt.decode(request.json['token'], secret, algorithms=['HS256', ])
    location = payload['device_location']
    if not location in results:
        abort(404, 'The specified device was not found')
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