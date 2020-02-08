from flask import request, jsonify, Blueprint, send_file
from subprocess import Popen, PIPE, STDOUT
import time
import os

from infra.utils import logger, get_global, get_job, set_global, set_job, get_db, copytree, is_installed


executor_api = Blueprint('executor_api', __name__)
log = logger()


@executor_api.route('/report', methods=['GET'])
def report():
    job_id = request.args.get('job_id')
    job_status = get_job(job_id)['status']
    if job_status == 'completed':
        return send_file(f'/app/tasks/{job_id}/payload')
    else:
        return job_status


@executor_api.route('/execute', methods=['PUT', 'POST'])
def execute():
    set_global('status', 'busy')

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
        'type': 'execute',
        'submitter_name': submitter_name,
        'submitter_url': submitter_url,
        'submitter_port': submitter_port,
        'id': job_id,
        'submission_time': submission_time,
        'filename': filename
    }

    set_job(job_id, job_params)

    log.info(f'installing: {filename} with id: {job_id}')

    task_path = f'tasks/{job_id}'
    os.mkdir(task_path)
    job_path = f'tasks/{job_id}/job_app'
    os.mkdir(job_path)
    copytree('/app/job_app', job_path)

    with open(f'{job_path}/job_pack/{filename}', 'w') as blob:
        rd = file.read().decode('ascii')
        blob.write(rd)

    set_job(job_id, {'status': 'installing'})
    cmd = f'bash infra/setup.sh {job_path}'
    Popen(cmd.split(), stderr=STDOUT, stdout=PIPE).communicate()

    while not is_installed():
        time.sleep(1)

    set_job(job_id, {'status': 'installed'})

    Popen(['python3', '/app/lib/executor.py', job_id], stderr=STDOUT, stdout=PIPE)

    reply = {
        'agent': get_global('agent_name'),
        'port': get_global('agent_port'),
        'payload': filename,
        'submission_time': submission_time,
        'id': job_id,
    }

    log.info(f'done installing {reply}')

    return jsonify(reply)
