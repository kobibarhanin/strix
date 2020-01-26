import sys
from infra.utils import logger

log = logger('kobi')

class Agent:

    def __init__(self) -> None:
        self._task_id = sys.argv[1]

    def id(self):
        return self._task_id

    def payload(self, output):
        log.info(f'payload of {self._task_id}: {output}')
        with open(f'_payload', 'w') as payload_file:
            payload_file.write(output)


