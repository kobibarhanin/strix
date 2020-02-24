from flask import request

from infra.utils import logger, set_global, set_job
from core.job import Job


log = logger()


def process_job(api):
    def wrapper():
        set_global('agent_status', 'busy')
        job = Job(request)
        response = api(job)
        return response
    return wrapper
