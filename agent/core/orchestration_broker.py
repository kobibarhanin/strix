import requests
from datetime import datetime
import time
from infra.utils import logger, set_job, get_job


log = logger()


def sync(job_id):
    while True:
        executors = list(get_job(job_id)['executors'])
        for executor in executors:
            name, timestamp, hb_status = heartbeat(executor)
            if hb_status:
                log.info(f'executor heartbeat: {name}, {timestamp}, {hb_status  }')
                executor['timestamp'] = str(timestamp)
                executor['status'] = hb_status
            else:
                log.info(f'no executor heartbeat for: {executor["name"]}')
        set_job(job_id, {'executors': executors})
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
