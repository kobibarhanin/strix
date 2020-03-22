import sys
import requests
import datetime


from infra.utils import logger, get_job, get_global,set_job


log = logger()


class Agent:

    def __init__(self, job_id=None) -> None:
        if not job_id:
            self._job_id = sys.argv[1]
        else:
            self._job_id = job_id

    def id(self):
        return self._job_id

    def payload(self, output):
        log.info(f'payload of {self._job_id}: {output}')
        with open(f'tasks/{self._job_id}/payload', 'w') as payload_file:
            payload_file.write(output)

    def complete(self):
        completion_time = str(datetime.datetime.now())

        set_job(self._job_id, {'status': 'completed', 'completion_time': completion_time})

        submitter_url = get_job(self._job_id)['submitter_url']
        submitter_port = get_job(self._job_id)['submitter_port']

        orchestrator_url = get_job(self._job_id)['orchestrator_url']
        orchestrator_port = get_job(self._job_id)['orchestrator_port']

        requests.post(f'http://{submitter_url}:{submitter_port}/complete',
                      params={'job_id': self._job_id,
                              'completion_time': completion_time,
                              'executor_name': get_global('agent_name'),
                              'executor_url': get_global('agent_url'),
                              'executor_port': get_global('agent_port')
                              })

        requests.post(f'http://{orchestrator_url}:{orchestrator_port}/complete',
                      params={'job_id': self._job_id,
                              'agent_name': get_global('agent_name'),
                              'completion_time': completion_time})

        self.report(f'completed executing job: {self._job_id}')

    def log(self, message, report=False):
        log.info(f'{message}')
        if report:
            self.report(message)

    def report(self, message, target=None):
        if target is None:
            target = get_global("tracker_host")
        requests.get(f'http://{target}:3000/log_report',
                     params={'agent_name': get_global('agent_name'),
                             'agent_log': message})

    def abort(self, job_id, agent_url, agent_port):
        requests.get(f'http://{agent_url}:{agent_port}/abort',
                     params={'job_id': job_id})

    def deorchestrate(self, job_id, agent_url, agent_port):
        requests.get(f'http://{agent_url}:{agent_port}/deorchestrate',
                     params={'job_id': job_id})