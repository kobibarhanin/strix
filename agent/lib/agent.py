import sys
import requests
from infra.utils import logger, get_job

log = logger('kobi')


class Agent:

    def __init__(self) -> None:
        self._task_id = sys.argv[1]

    def id(self):
        return self._task_id

    def payload(self, output):
        log.info(f'payload of {self._task_id}: {output}')
        with open(f'tasks/{self._task_id}/payload', 'w') as payload_file:
            payload_file.write(output)

    def complete(self):
        submitter = get_job(self._task_id)['submitter']
        requests.post(f'http://{submitter}:5000/complete',
                      params={'task_id': self._task_id})
