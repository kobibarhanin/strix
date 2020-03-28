from flask import request, Blueprint
from infra.utils import get_job, set_job, logger, get_db
from core.agent import Agent

log = logger()

common_api = Blueprint('common_api', __name__)


@common_api.route('/complete', methods=['POST'])
def complete():
    try:
        job_id = request.args.get('job_id')
        completing_agent = request.args.get('agent_name')
        job_params = {
            'job_status': 'completed',
            'completion_time': request.args.get('completion_time'),
            'executor_name': request.args.get('executor_name'),
            'executor_url': request.args.get('executor_url'),
            'executor_port': request.args.get('executor_port')
        }
        set_job(job_id, job_params)
        if get_job(job_id)['role'] == 'orchestrate':
            agent = Agent(job_id)
            for executor in list(get_job(job_id)['executors']):
                if executor['name'] != completing_agent:
                    agent.abort(job_id, executor['url'], executor['port'])
        return str(job_params)
    except Exception as e:
        log.exception('unable to complete')
        return {}


@common_api.route('/get_jobs')
def get_jobs():
    reply = dict()
    for job in get_db('jobs'):
        if 'completion_time' in job:
            job['update_time'] = job['completion_time']
        else:
            job['update_time'] = job['submission_time']
        reply[job['id']] = job
    return reply


@common_api.route('/job_status')
def job_status():
    job_id = request.args.get('job_id')
    return get_job(job_id)['job_status']
