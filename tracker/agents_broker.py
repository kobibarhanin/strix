import requests
from datetime import datetime
import time
import pymongo


db_host = 'bitz_db'
agents = pymongo.MongoClient(f'mongodb://{db_host}:27017/')['agentsDb']['agent']


def sync():
    while True:
        for agent in agents.find():
            name, timestamp, hb_status = heartbeat(agent)
            if hb_status:
                agents.update({'name': name}, {'$set': {'timestamp': timestamp, 'status': hb_status}})
                print(f'heartbeat: {name} , {timestamp}, {hb_status}')
        time.sleep(5)


def heartbeat(agent):
    try:
        response = requests.get(f'http://{agent["url"]}:{agent["port"]}/heartbeat').json()
    except Exception:
        print(f'error connecting to: {agent["name"]} on {agent["port"]}')
        return '', '', ''
    name, status, ts = response.values()
    timestamp = datetime.fromtimestamp(float(response['time']))
    return name, timestamp, status
