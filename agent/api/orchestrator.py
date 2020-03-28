from flask import request, Blueprint, jsonify
from threading import Thread
import time
import requests
import json

from infra.utils import logger, get_global, set_global, set_job, get_db
from core.agent import Agent
from core.orchestration_broker import sync
from infra.decorators import process_job

orchestrator_api = Blueprint('orchestrator_api', __name__)
log = logger()


@orchestrator_api.route('/orchestrate', methods=['PUT', 'POST', 'GET'])
@process_job
def orchestrate(job):
    job_id = job.job_id
    agent = Agent(job_id=job_id, role='orchestrate')

    job.set('start_time', time.time())

    git_repo = job.get('git_repo')
    file_name = job.get('file_name')

    agent.log(f'orchestrating', report=True, job_id=job_id)

    exec_agents = json.loads(requests.get(f'http://{get_global("tracker_host")}:3000/assign_agents',
                                          params={
                                              'source': job.get('submitter_name'),
                                              'orchestrator': get_global('agent_name'),
                                              'required': 2
                                          }).content.decode("ascii"))

    job.set('executors', exec_agents)
    agent.report_job(job_id, f'executors: {exec_agents}')

    for exec_agent in exec_agents:
        agent.log(f'sending to executor: {exec_agent["name"]}', report=True, job_id=job_id)
        time.sleep(5)
        try:
            requests.get(f'http://{exec_agent["url"]}:{exec_agent["port"]}/execute',
                         params={
                             'git_repo': git_repo,
                             'file_name': file_name,
                             'job_id': job_id,
                             'submission_time': job.get('submission_time'),
                             'submitter_name': job.get('submitter_name'),
                             'submitter_url': job.get('submitter_url'),
                             'submitter_port': job.get('submitter_port'),
                             'orchestrator_name': get_global('agent_name'),
                             'orchestrator_url': get_global('agent_url'),
                             'orchestrator_port': get_global('agent_port')
                         },
                         timeout=0.0000000001)
        except requests.exceptions.ReadTimeout:
            pass

    time.sleep(3)
    Thread(target=sync, kwargs={'job_id': job_id}).start()

    set_global('agent_status', 'connected')

    return f'sent job {job.job_id} to executors: {exec_agents}'
