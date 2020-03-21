from flask import request, Blueprint, jsonify
from threading import Thread
import time
import requests
import json
import os


from infra.utils import logger, get_global, set_global, set_job, get_db
from core.agent import Agent
from core.orchestration_broker import sync
from infra.decorators import process_job


orchestrator_api = Blueprint('orchestrator_api', __name__)
log = logger()


@orchestrator_api.route('/jobs_orchestrated')
def jobs_orchestrated():
    reply = list()
    for job in get_db('jobs'):
        if job['job_type'] == 'orchestrate':
            executors = list(job['executors'])
            for executor in executors:
                reply.append(executor)
    return jsonify(reply)


@orchestrator_api.route('/orchestrate', methods=['PUT', 'POST'])
@process_job
def orchestrate(job):

    job_id = job.job_id
    agent = Agent(job_id)
    job.set('job_type', 'orchestrate')
    job.set('start_time', time.time())

    filename = job.get('filename')
    file = request.files[filename]

    try:
        with open(f'/app/temp/{filename}', 'wb') as blob:
            rd = file.read()
            blob.write(rd)
    except Exception as e:
        agent.report(f'{e}')

    agent.report(f'orchestrating job: {job_id}, payload: {filename}')
    exec_agents = json.loads(requests.get(f'http://{get_global("tracker_host")}:3000/assign_agents',
                                          params={'source': job.get('submitter_name'),
                                                  'orchestrator': get_global('agent_name'),
                                                  'required': 2}).content.decode("ascii"))

    job.set('executors', exec_agents)
    agent.report(f'executors: {exec_agents}')

    for exec_agent in exec_agents:

        agent.log(f'sending job: {job_id}, to executor: {exec_agent["name"]}, at {exec_agent["url"]}:{exec_agent["port"]}', report=True)

        payload = open(f'/app/temp/{filename}', 'rb')
        response = requests.post(f'http://{exec_agent["url"]}:{exec_agent["port"]}/execute',
                                 params={'filename': filename,
                                         'job_id': job_id,
                                         'submission_time': job.get('submission_time'),
                                         'submitter_name': job.get('submitter_name'),
                                         'submitter_url': job.get('submitter_url'),
                                         'submitter_port': job.get('submitter_port'),
                                         'orchestrator_name': get_global('agent_name'),
                                         'orchestrator_url': get_global('agent_url'),
                                         'orchestrator_port': get_global('agent_port')
                                         },
                                 files={filename: payload})
        payload.close()
        log.info(f'response from executor: {response.json()}')

    time.sleep(3)
    Thread(target=sync, kwargs={'job_id': job_id}).start()

    if os.path.isfile(f'/app/temp/{filename}'):
        os.remove(f'/app/temp/{filename}')

    set_global('agent_status', 'connected')

    return {}
