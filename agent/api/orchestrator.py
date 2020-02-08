from flask import request, Blueprint
import time
import datetime
import requests
import json

from infra.utils import logger, get_global, get_job, set_global, set_job, get_db, copytree, is_installed


orchestrator_api = Blueprint('orchestrator_api', __name__)

log = logger()


@orchestrator_api.route('/orchestrate', methods=['PUT', 'POST'])
def orchestrate():
    set_global('status', 'busy')

    file = request.files['file_blob']

    filename = request.args.get('filename')
    job_id = request.args.get('task_id')
    submitter_name = request.args.get('submitter_name')
    submitter_url = request.args.get('submitter_url')
    submitter_port = request.args.get('submitter_port')
    submission_time = request.args.get('submission_time')
    file = request.files[filename]

    job_params = {
        'status': 'received',
        'start_time': time.time(),
        'type': 'orchestrate',
        'submitter_name': submitter_name,
        'submitter_url': submitter_url,
        'submitter_port': submitter_port,
        'id': job_id,
        'submission_time': submission_time,
        'filename': filename
    }

    set_job(job_id, job_params)

    # =================================================================

    exec_agent = json.loads(requests.get(f'http://{get_global("tracker_host")}:3000/assign_agent',
                                         params={'source': submitter_name, 'orchestrator': get_global('agent_name')}
                                         ).content.decode("ascii"))

    log.info(f'executing agent: {exec_agent["name"]} at {exec_agent["url"]}:{exec_agent["port"]}')

    submission_time = str(datetime.datetime.now())

    job_params = {
        'type': 'submitted',
        'status': 'submitted',
        'assigned_agent': exec_agent,
        'id': job_id,
        'payload': file.filename,
        'submission_time': submission_time
    }

    set_job(job_id, job_params)

    response = requests.post(f'http://{exec_agent["url"]}:{exec_agent["port"]}/execute',
                             params={'filename': file.filename,
                                     'task_id': job_id,
                                     'submission_time': submission_time,
                                     'submitter_name': get_global('agent_name'),
                                     'submitter_url': get_global('agent_url'),
                                     'submitter_port': get_global('agent_port')
                                     },
                             files={file.filename: file})

    set_global('status', 'ready')

    return response.json()
