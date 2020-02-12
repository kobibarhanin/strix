import sys
import requests
import datetime

from infra.utils import logger, get_job, get_global,set_job

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

        set_job(self._task_id, {'status': 'completed', 'completion_time':completion_time})

        submitter_url = get_job(self._task_id)['submitter_url']
        submitter_port = get_job(self._task_id)['submitter_port']

        orchestrator_url = get_job(self._task_id)['orchestrator_url']
        orchestrator_port = get_job(self._task_id)['orchestrator_port']

        requests.post(f'http://{submitter_url}:{submitter_port}/complete',
                      params={'task_id': self._task_id,
                              'completion_time': completion_time,
                              'executor_name': get_global('agent_name'),
                              'executor_url': get_global('agent_url'),
                              'executor_port': get_global('agent_port')
                              })

        requests.post(f'http://{orchestrator_url}:{orchestrator_port}/complete',
                      params={'task_id': self._task_id,
                              'agent_name': get_global('agent_name'),
                              'completion_time': completion_time})

        self.report(f'completed executing job: {self._task_id}')

    def report(self, message, target=get_global("tracker_host")):
        requests.get(f'http://{target}:3000/log_report',
                     params={'agent_name': get_global('agent_name'),
                             'agent_log': message})

    def abort(self, job_id, agent_url, agent_port):
        requests.get(f'http://{agent_url}:{agent_port}/abort',
                     params={'job_id': job_id})
