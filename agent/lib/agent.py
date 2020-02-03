import sys
import requests
import datetime

from infra.utils import logger, get_job,get_global

log = logger('kobi')


class Agent:

    def __init__(self, task_id=None) -> None:
        if not task_id:
            self._task_id = sys.argv[1]
        else:
            self._task_id = task_id

    def id(self):
        return self._task_id

    def payload(self, output):
        log.info(f'payload of {self._task_id}: {output}')
        with open(f'tasks/{self._task_id}/payload', 'w') as payload_file:
            payload_file.write(output)

    def complete(self):
        submitter_url = get_job(self._task_id)['submitter_url']
        submitter_port = get_job(self._task_id)['submitter_port']
        requests.post(f'http://{submitter_url}:{submitter_port}/complete',
                      params={'task_id': self._task_id, 'completion_time': str(datetime.datetime.now())})
