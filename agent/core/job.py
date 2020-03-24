from typing import Any
import uuid

from infra.utils import logger, set_job
from infra.consts import JOB_PARAMS

log = logger()


class Job:

    def __init__(self, request) -> None:

        self.config = dict()
        try:
            jid = request.args.get('job_id')
            self.job_id = jid if jid is not None else uuid.uuid4().hex
            for arg in request.args.keys():
                if arg in JOB_PARAMS:
                    self.config[arg] = request.args.get(arg)
                    set_job(self.job_id, request.args)

            self.set('job_status', 'created')
        except Exception as e:
            self.set('job_status', 'failed')
            raise Exception(f'failed to create job: {e}')

    def set(self, key: str, value: Any) -> None:
        self.config[key] = value
        set_job(self.job_id, {key: value})

    def set_many(self, values):
        for k, v in values.items():
            self.set(k, v)

    def get(self, key: str) -> Any:
        return self.config[key]
