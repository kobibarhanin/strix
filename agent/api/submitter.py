from flask import request, jsonify, Blueprint

import datetime
import uuid
import requests
import json

from infra.utils import logger, get_global, get_job, set_global, set_job, get_db, copytree, is_installed
from core.agent import Agent

submitter_api = Blueprint('submitter_api', __name__)
log = logger()


@submitter_api.route('/jobs_submitted')
def jobs_submitted():
    jobs = dict(get_db('jobs')[0])
    reply = dict()
    for id, job in jobs.items():
        if job['job_type'] == 'submitted':
            reply[id] = job
    return reply


@submitter_api.route('/get_report', methods=['GET'])
def get_report():
    job_id = request.args.get('id')
    executor_url = get_job(job_id)['executor_url']
    executor_port = get_job(job_id)['executor_port']
    return requests.get(f'http://{executor_url}:{executor_port}/report',
                        params={'job_id': job_id}).content.decode("ascii")


@submitter_api.route('/submit', methods=['PUT', 'POST'])
def submit():
    job_id = uuid.uuid4().hex
    file = request.files['file_blob']

    if get_global('agent_status') == 'disabled':
        return jsonify({'status': 'disabled'})

    agent = Agent(job_id)
    agent.report(f'submitting job: {job_id}, payload_file: {file.filename}')

    orchestrator_agents = json.loads(requests.get(f'http://{get_global("tracker_host")}:3000/assign_agents',
                                                  params={'source': get_global('agent_name'),
                                                          'required': 1}
                                                  ).content.decode("ascii"))

    # TODO: assuming 1 orchestrator agent
    orchestrator_agent = orchestrator_agents[0]

    log.info(f'orchestrator agent: {orchestrator_agent["name"]} at {orchestrator_agent["url"]}:{orchestrator_agent["port"]}')

    log.info(f'file = {file}, file.filename = {file.filename}')

    submission_time = str(datetime.datetime.now())

    job_params = {
        'job_type': 'submitted',
        'job_status': 'submitted',
        'assigned_agent': orchestrator_agent,
        'job_id': job_id,
        'payload': file.filename,
        'submission_time': submission_time,
    }

    set_job(job_id, job_params)

    agent.report(f'sending job: {job_id}, to orchestrator: {orchestrator_agent}')

    requests.post(f'http://{orchestrator_agent["url"]}:{orchestrator_agent["port"]}/orchestrate',
                  params={'filename': file.filename,
                          'job_id': job_id,
                          'submission_time': submission_time,
                          'submitter_name': get_global('agent_name'),
                          'submitter_url': get_global('agent_url'),
                          'submitter_port': get_global('agent_port')
                          },
                  files={file.filename: file})

    return {}
