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
        completion_time = str(datetime.datetime.now())

        submitter_url = get_job(self._task_id)['submitter_url']
        submitter_port = get_job(self._task_id)['submitter_port']

        orchestrator_url = get_job(self._task_id)['orchestrator_url']
        orchestrator_port = get_job(self._task_id)['orchestrator_port']

        requests.post(f'http://{submitter_url}:{submitter_port}/complete',
                      params={'task_id': self._task_id, 'completion_time': completion_time})

        requests.post(f'http://{orchestrator_url}:{orchestrator_port}/complete',
                      params={'task_id': self._task_id, 'completion_time': completion_time})

        requests.get(f'http://{get_global("tracker_host")}:3000/log_report',
                     params={'agent_name': get_global('agent_name'),
                             'agent_log': f'completed executing job: {self._task_id}'})
