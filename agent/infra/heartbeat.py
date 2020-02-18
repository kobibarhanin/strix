from infra.utils import logger, get_global, get_job
from datetime import datetime


log = logger()


class Heartbeat:
    def __init__(self) -> None:
        self.agent_name = get_global('agent_name')
        self.agent_status = get_global('agent_status')
        self.timestamp = str(datetime.now())


class ExecutorHeartbeat(Heartbeat):
    def __init__(self, job_id) -> None:
        super().__init__()
        self.job_status = get_job(job_id)['job_status']
        self.job_id = get_job(job_id)['job_id']
        self.filename = get_job(job_id)['filename']
        self.submission_time = get_job(job_id)['submission_time']

# vars(Heartbeat())
# vars(ExecutorHeartbeat(job_id))

