from flask import request, jsonify, Blueprint
import datetime
import requests
import json

from infra.utils import logger, get_global, get_job, get_db
from core.agent import Agent
from infra.decorators import process_job

submitter_api = Blueprint('submitter_api', __name__)
log = logger()


@submitter_api.route('/jobs_submitted')
def jobs_submitted():
    reply = dict()
    for job in get_db('jobs'):
        if job['job_type'] == 'submitted':
            reply[job['id']] = job
    return reply


@submitter_api.route('/get_report', methods=['GET'])
def get_report():
    job_id = request.args.get('id')
    executor_url = get_job(job_id)['executor_url']
    executor_port = get_job(job_id)['executor_port']
    return requests.get(f'http://{executor_url}:{executor_port}/report',
                        params={'job_id': job_id}).content.decode("ascii")


def request_orchestrator(agent, required):
    agent.log(f'requesting orchestrating agents', report=True)
    orchestrator_agents = json.loads(requests.get(f'http://{get_global("tracker_host")}:3000/assign_agents',
                                                  params={'source': get_global('agent_name'),
                                                          'required': required}).content.decode("ascii"))[0]
    agent.log(f'acquired orchestrating agents:\n{orchestrator_agents}', report=True)
    return orchestrator_agents


@submitter_api.route('/submit', methods=['PUT', 'POST', 'GET'])
@process_job
def submit(job):
    try:
        job_id = job.job_id
        agent = Agent(job_id)

        git_repo = job.get('git_repo')
        file_name = job.get('file_name')

        job_params = {
            'job_type': 'submitted',
            'job_status': 'submitted',
            'submission_time': str(datetime.datetime.now()),
        }
        job.set_many(job_params)

        agent.report(f'submitting job:\n id: {job_id}\n url:{git_repo}\n file:{file_name}')

        orchestrator_agent = request_orchestrator(agent, 1)

        job.set('assigned_agent',orchestrator_agent)
        agent.report(f'sending job: {job_id}, to orchestrator: {orchestrator_agent}')

        requests.get(f'http://{orchestrator_agent["url"]}:{orchestrator_agent["port"]}/orchestrate',
                     params={
                         'git_repo': git_repo,
                         'file_name': file_name,
                         'job_id': job_id,
                         'submission_time': job_params['submission_time'],
                         'submitter_name': get_global('agent_name'),
                         'submitter_url': get_global('agent_url'),
                         'submitter_port': get_global('agent_port')
                     })

        agent.set('agent_status', 'connected')

    except Exception as e:
        agent.log(e)

    return {}
