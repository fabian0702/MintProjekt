from pymongo import MongoClient, DESCENDING
from os import environ
from datetime import datetime

PASSWORD = environ.get('MONGO_ROOT_PASSWORD', 'password')

# Connection to MongoDB with authentication
database = MongoClient('mongodb', 27017, username='root', password=PASSWORD)['mint']

def addData(location:str, data:int):
    return database['pastdata'].insert_one({'location':location, 'timestamp':int(datetime.now().timestamp()/60)*60, 'data':data})

def getData(location:str, count:int=5) -> list[int]:
    return [x['data'] for x in database['pastdata'].find({'location':location}, sort=[('timestamp', DESCENDING)], limit=count)]

def getDataByTimestamp(location:str, timestamp:float) -> int:
    data = [x['data'] for x in database['pastdata'].find({'location':location, 'timestamp':timestamp}, limit=1)]
    return data[0] if len(data) else None

def chageCoefficients(location:str, correlationCoefficients:list[float]):
    database['locations'].update_one({'location':location}, {'location':location, 'correlationCoefficients':correlationCoefficients})

def addLocation(location:str, correlationCoefficients:list[float]):
    return database['locations'].insert_one({'location':location, 'correlationCoefficients':correlationCoefficients})

def getLocation(location:str) -> list:
    results = list(database['locations'].find({'location':location}, limit=1))
    return results[0] if len(results) else None