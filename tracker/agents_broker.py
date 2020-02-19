import requests
import time
import pymongo
import os

from infra.utils import logger

db_host = os.environ['DB_CTX'] if 'DB_CTX' in os.environ else 'bitz_db'
agents = pymongo.MongoClient(f'mongodb://{db_host}:27017/')['agentsDb']['agent']

log = logger()


def sync():
    while True:
        for agent in agents.find():
            response = heartbeat(agent)
            if response:
                agents.update({'name': response['agent_name'],}, {'$set': {'timestamp': response['timestamp'], 'status': response['agent_status']}})
                log.info(f'heartbeat -> {response}')
        time.sleep(5)


def heartbeat(agent):
    try:
        response = requests.get(f'http://{agent["url"]}:{agent["port"]}/heartbeat').json()
    except Exception as e:
        log.info(f'error = {e}')
        print(f'error connecting to: {agent["name"]} on {agent["port"]}')
        return '', '', ''
    return dict(response)
