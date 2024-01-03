import sqlite3
from datetime import datetime

db = sqlite3.connect("some.db", check_same_thread=False)
cur = db.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS historical_data ( location TEXT PRIMARY KEY NOT NULL, timestamp FLOAT NOT NULL UNIQUE, data TEXT NOT NULL );''')

def addData(location:str, data:list[int]):
    cur.execute('''INSERT INTO historical_data VALUES(?,?,?)''', (location, datetime.timestamp(), ','.join(data)))
    cur.execute('''DELETE FROM historical_data WHERE timestamp < ?''', (datetime.timestamp()))

def getRecentData(location:str, count:int=5):
    return [list(map(int, x.split(','))) for x in cur.execute('''SELECT data FROM historical_data WHERE location=? ORDER BY timestamp DESC LIMIT ?''', (location, count))]
