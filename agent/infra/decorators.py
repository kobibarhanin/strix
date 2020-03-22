from flask import request

from infra.utils import logger, set_global, set_job
from core.job import Job


log = logger()


def process_job(api):
    def wrapper():
        set_global('agent_status', 'busy')
        try:
            job = Job(request)
            log.info('job: %s', job)
            response = api(job)
            return response
        except Exception as e:
            log.info('Error in process_job ' + str(e))
            return 'job failed'
    return wrapper
