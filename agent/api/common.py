from flask import request, Blueprint
from infra.utils import get_job, set_job, logger
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
        if get_job(job_id)['job_type'] == 'orchestrate':
            agent = Agent(job_id)
            for executor in list(get_job(job_id)['executors']):
                if executor['name'] != completing_agent:
                    agent.abort(job_id, executor['url'], executor['port'])
        return str(job_params)
    except Exception as e:
        log.exception('unable to complete')
        return {}