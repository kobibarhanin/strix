from flask import request, Blueprint, jsonify
import time
import requests
import json

from infra.utils import logger, get_global, set_global, set_job
from lib.agent import Agent


orchestrator_api = Blueprint('orchestrator_api', __name__)

log = logger()


@orchestrator_api.route('/orchestrate', methods=['PUT', 'POST'])
def orchestrate():

    set_global('status', 'busy')

    filename = request.args.get('filename')
    job_id = request.args.get('task_id')
    submitter_name = request.args.get('submitter_name')
    submitter_url = request.args.get('submitter_url')
    submitter_port = request.args.get('submitter_port')
    submission_time = request.args.get('submission_time')
    file = request.files[filename]

    log.info(f'file = {file}, file.filename = {file.filename}, filename = {filename}, request.files = {request.files}')

    agent = Agent(job_id)

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

    agent.report(f'orchestrating job: {job_id}')

    exec_agent = json.loads(requests.get(f'http://{get_global("tracker_host")}:3000/assign_agent',
                                         params={'source': submitter_name,
                                                 'orchestrator': get_global('agent_name')}
                                         ).content.decode("ascii"))

    log.info(f'executing agent: {exec_agent["name"]} at {exec_agent["url"]}:{exec_agent["port"]}')

    job_params = {
        'executor_name': exec_agent["name"],
        'executor_url': exec_agent["url"],
        'executor_port': exec_agent["port"],
    }

    set_job(job_id, job_params)

    agent.report(f'sending job: {job_id}, to executor: {exec_agent["name"]}')

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
                             files={file.filename: file})

    log.info(f'response from executor: {response.json()}')
    set_global('status', 'ready')

    return jsonify(response.json())
