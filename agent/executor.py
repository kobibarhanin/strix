import subprocess
import sys
import time

from infra.utils import set_job, set_global

exe_file = sys.argv[1]
job_id = sys.argv[2]

set_job(job_id, 'status', 'running')

job_path = f'tasks/{job_id}'
subprocess.call(['python', f'{job_path}/{exe_file}', job_id])

set_job(job_id, 'status', 'completed')
set_job(job_id, 'end_time', time.time())

set_global('status', 'ready')