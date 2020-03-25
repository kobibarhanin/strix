from flask import request, jsonify

from infra.utils import logger, set_global, set_job
from core.job import Job
from core.agent import Agent


log = logger()


def process_job(api):
    def wrapper():

        if Agent.get('agent_status') == 'disabled':
            return jsonify({'status': 'disabled'})
        Agent.set('agent_status', 'busy')

        log.info(f'processing request: \n'
                 f'{[{k:v} for k,v in request.args.items()]}\n'
                 f'role: {api.__name__}')

        try:
            job = Job(request)
            job.set('role', api.__name__)
            log.info(f'job object created with id: {job.job_id}')
            return api(job)
        except Exception as e:
            log.info(f'error in job processing: {e}', report=True)
    return wrapper
