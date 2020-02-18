from flask import request, Blueprint, jsonify
from threading import Thread
import time
import requests
import json
import os

from infra.utils import logger, get_global, set_global, set_job, get_db
from lib.agent import Agent
from core.orchestration_broker import sync

orchestrator_api = Blueprint('orchestrator_api', __name__)

log = logger()


@orchestrator_api.route('/jobs_orchestrated')
def jobs_executed():
    jobs = dict(get_db('jobs')[0])
    reply = list()
    for _, job in jobs.items():
        if job['type'] == 'orchestrate':
            executors = list(job['executors'])
            for executor in executors:
                reply.append(executor)
    return jsonify(reply)


@orchestrator_api.route('/orchestrate', methods=['PUT', 'POST'])
def orchestrate():
    set_global('agent_status', 'busy')

    filename = request.args.get('filename')
    job_id = request.args.get('task_id')
    submitter_name = request.args.get('submitter_name')
    submitter_url = request.args.get('submitter_url')
    submitter_port = request.args.get('submitter_port')
    submission_time = request.args.get('submission_time')
    file = request.files[filename]

    agent = Agent(job_id)

    try:
        with open(f'/app/temp/{filename}', 'wb') as blob:
            # rd = file.read().decode('ascii')
            rd = file.read()
            blob.write(rd)
    except Exception as e:
        agent.report(f'{e}')

    job_params = {
        'status': 'received',
        'start_time': time.time(),
        'type': 'orchestrate',
        'submitter_name': submitter_name,
        'submitter_url': submitter_url,
        'submitter_port': submitter_port,
        'id': job_id,
        'submission_time': submission_time,
        'filename': filename
    }

    set_job(job_id, job_params)
    agent.report(f'orchestrating job: {job_id}, payload: {filename}')

    exec_agents = json.loads(requests.get(f'http://{get_global("tracker_host")}:3000/assign_agents',
                                          params={'source': submitter_name,
                                                  'orchestrator': get_global('agent_name'),
                                                  'required': 2}).content.decode("ascii"))

    set_job(job_id, {'executors': exec_agents})
    agent.report(f'executors: {exec_agents}')
    log.info(f'executors: {exec_agents}')

    for exec_agent in exec_agents:

        log.info(f'executing agent: {exec_agent["name"]} at {exec_agent["url"]}:{exec_agent["port"]}')

        agent.report(f'sending job: {job_id}, to executor: {exec_agent["name"]}')

        payload = open(f'/app/temp/{filename}', 'rb')
        response = requests.post(f'http://{exec_agent["url"]}:{exec_agent["port"]}/execute',
                                 params={'filename': file.filename,
                                         'task_id': job_id,
                                         'submission_time': submission_time,
                                         'submitter_name': submitter_name,
                                         'submitter_url': submitter_url,
                                         'submitter_port': submitter_port,
                                         'orchestrator_name': get_global('agent_name'),
                                         'orchestrator_url': get_global('agent_url'),
                                         'orchestrator_port': get_global('agent_port')
                                         },
                                 files={file.filename: payload})
        payload.close()
        log.info(f'response from executor: {response.json()}')

    time.sleep(3)
    Thread(target=sync, kwargs={'job_id': job_id}).start()

    if os.path.isfile(f'/app/temp/{filename}'):
        os.remove(f'/app/temp/{filename}')

    set_global('agent_status', 'connected')

    return {}
