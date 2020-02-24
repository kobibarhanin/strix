from typing import Any
from infra.utils import logger, set_job
from infra.consts import JOB_PARAMS

log = logger()


class Job:

    def __init__(self, request) -> None:

        self.config = dict()
        self.job_id = request.args.get('job_id')
        self.set('job_status', 'received')

        for arg in request.args.keys():
            if arg in JOB_PARAMS:
                self.config[arg] = request.args.get(arg)
                set_job(self.job_id, request.args)

        if 'filename' in self.config.keys():
            self.file = request.files[self.config['filename']]

    def set(self, key: str, value: Any) -> None:
        log.info(f'setting: {key} = {value}')
        self.config[key] = value
        set_job(self.job_id, {key: value})

    def get(self, key: str) -> Any:
        return self.config[key]
