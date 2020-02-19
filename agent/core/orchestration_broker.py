import requests
from datetime import datetime
import time
from infra.utils import logger, set_job, get_job


log = logger()


def sync(job_id):
    log.info(f'initiate executors syncing')
    try:
        while True:
            executors = list(get_job(job_id)['executors'])
            for executor in executors:
                try:
                    response = heartbeat(executor, job_id)
                    if response:
                        executor['timestamp'] = response['time']
                        executor['agent_status'] = response['agent_status']
                        executor['job_status'] = response['job_status']
                        executor['job_id'] = response['job_id']
                        executor['filename'] = response['filename']
                        executor['submission_time'] = response['submission_time']
                    else:
                        log.info(f'no executor heartbeat for: {executor["name"]}')
                except Exception as e:
                    pass
            if get_job(job_id)['job_status'] == 'completed':
                for executor in executors:
                    executor['agent_status'] = 'offline'
                set_job(job_id, {'executors': executors})
                break
            set_job(job_id, {'executors': executors})
            time.sleep(5)

    except Exception as e:
        log.exception(f'error in sync: {e}')


def heartbeat(agent, job_id):
    try:
        response = requests.get(f'http://{agent["url"]}:{agent["port"]}/exec_heartbeat', params={'job_id': job_id}).json()
    except Exception:
        print(f'error connecting to: {agent["name"]} on {agent["port"]}')
        return '', '', ''
    return dict(response)
