import sys
import time

from infra.utils import set_job, set_global, get_job, logger

log = logger()
job_id = sys.argv[1]


set_job(job_id, {'job_status':'executing'})
log.info(f'executor running on: {job_id}')


try:
    from job_pack import run
    run(job_id)
    set_job(job_id, {'job_status': 'completed'})
except Exception as e:
    log.info(f'error = {e}')
    set_job(job_id, {'job_status': 'failed'})

set_job(job_id, {'end_time': time.time()})
set_global('agent_status', 'connected')
