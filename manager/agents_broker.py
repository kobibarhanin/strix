import requests
from datetime import datetime
import time
import pymongo


agents = pymongo.MongoClient("mongodb://localhost:27017/")['agentsDb']['agent']


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


def register_agents(agents_pool, drop=False):
    if drop:
        agents.drop()
    agents_list = []
    for agent in agents_pool:
        name, timestamp, hb = heartbeat(agent)
        agents_list.append({'name': name, 'timestamp': timestamp, 'port': agent['port'], 'url': agent['url'], 'status': hb})
    agents.insert_many(agents_list)
    for agent in agents.find():
        print(f'registered: {agent["name"]} on {agent["port"]} is {agent["status"]}')


# def execute(port, cmd):
#     response = requests.get(f'http://0.0.0.0:{port}/execute', params={'cmd': cmd})
#     print(f'result: {response} , body: {response.content}')


if __name__ == '__main__':
    base_url = 'http://10.0.2.5'
    # base_url = 'http://0.0.0.0'
    agents_to_register = [{'name': 'bitz', 'url': base_url, 'port': 5000}, {'name': 'bitz_2', 'url': base_url, 'port': 5001}]
    register_agents(agents_to_register, drop=True)
    # sync()
