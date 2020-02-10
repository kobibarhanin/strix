from flask import request, jsonify, Blueprint, send_file
from subprocess import Popen, PIPE, STDOUT
import time
import os
import requests

from infra.utils import logger, get_global, get_job, set_global, set_job, get_db, copytree, is_installed
from lib.agent import Agent


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
    try:
        set_global('status', 'busy')

        filename = request.args.get('filename')
        job_id = request.args.get('task_id')
        submitter_name = request.args.get('submitter_name')
        submitter_url = request.args.get('submitter_url')
        submitter_port = request.args.get('submitter_port')

        orchestrator_name = request.args.get('orchestrator_name')
        orchestrator_url = request.args.get('orchestrator_url')
        orchestrator_port = request.args.get('orchestrator_port')

        submission_time = request.args.get('submission_time')
        file = request.files[filename]

        agent = Agent(job_id)

        job_params = {
            'status': 'received',
            'start_time': time.time(),
            'type': 'execute',
            'submitter_name': submitter_name,
            'submitter_url': submitter_url,
            'submitter_port': submitter_port,
            'orchestrator_name': orchestrator_name,
            'orchestrator_url': orchestrator_url,
            'orchestrator_port': orchestrator_port,
            'id': job_id,
            'submission_time': submission_time,
            'filename': file.filename
        }

        set_job(job_id, job_params)
        set_job(job_id, {'status': 'installing'})

        log.info(f'installing: {file.filename} with id: {job_id}')
        agent.report(f'installing {file.filename}, for job: {job_id}')

        task_path = f'tasks/{job_id}'
        os.mkdir(task_path)
        job_path = f'tasks/{job_id}/job_app'
        os.mkdir(job_path)
        copytree('/app/job_app', job_path)

        with open(f'{job_path}/job_pack/{file.filename}', 'w') as blob:
            rd = file.read().decode('ascii')
            blob.write(rd)

        cmd = f'bash infra/setup.sh {job_path}'
        Popen(cmd.split(), stderr=STDOUT, stdout=PIPE).communicate()

        time_ctr = 0
        while not is_installed():
            time_ctr += 1
            time.sleep(1)
            if time_ctr >= 10:
                err_msg = f'failed installing job {job_id}, aborting'
                set_job(job_id, {'status': 'failed'})
                set_global('status', 'ready')
                agent.report(err_msg)
                return

        set_job(job_id, {'status': 'installed'})

        agent.report(f'executing job: {job_id}')

        Popen(['python3', '/app/lib/executor.py', job_id], stderr=STDOUT, stdout=PIPE)

        reply = {
            'name': get_global('agent_name'),
            'url': get_global('agent_url'),
            'port': get_global('agent_port'),
            'payload': file.filename,
            'submission_time': submission_time,
            'id': job_id,
        }

        log.info(f'done installing {reply}')

        return jsonify(reply)

    except Exception as e:
        log.info(f'error: {e}')
        return f'error: {e}'
