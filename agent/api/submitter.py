from flask import request, jsonify, render_template, Blueprint
import random
import string
import time
import datetime
import os
import uuid
import requests
import json

from infra.utils import logger, get_global, get_job, set_global, set_job, get_db, copytree, is_installed


submitter_api = Blueprint('submitter_api', __name__)
log = logger()


@submitter_api.route('/')
def get():
    return render_template('agent_view.html',
                           version=''.join(random.choices(string.ascii_uppercase + string.digits, k=10)),
                           agent=os.environ['AGENT_NAME'])


@submitter_api.route('/logs')
def logs():
    log_flow = []
    f = open('agent.log', 'r')
    limit = 20
    for line in reversed(list(f)):
        if limit == 0:
            break
        if 'logs' in line or 'heartbeat' in line or 'jobs' in line or 'connectivity' in line:
            continue
        log_flow.append(line)
        limit -= 1
    f.close()
    return jsonify(log_flow)


@submitter_api.route('/connectivity')
def connectivity():
    current_time = time.time()
    try:
        heartbeat_last = float(get_global('heartbeat_last'))
    except Exception:
        return {'status': 'disconnected'}
    if current_time - heartbeat_last > 10:
        return {'status': 'disconnected'}
    else:
        return {'status': 'connected'}


@submitter_api.route('/jobs')
def jobs():
    jobs = dict(get_db('jobs')[0])
    reply = dict()
    for id, job in jobs.items():
        if job['type'] == 'submitted':
            reply[id] = job
    return reply


@submitter_api.route('/get_report', methods=['GET'])
def get_report():
    job_id = request.args.get('id')
    assigned_agent = get_job(job_id)['assigned_agent']
    return requests.get(f'http://{assigned_agent["url"]}:{assigned_agent["port"]}/report',
                        params={'job_id': job_id}).content.decode("ascii")


@submitter_api.route('/complete', methods=['POST'])
def complete():
    job_id = request.args.get('task_id')
    completion_time = request.args.get('completion_time')
    job_params = {
        'status': 'completed',
        'completion_time': completion_time
    }
    set_job(job_id, job_params)
    return str(job_params)


@submitter_api.route('/submit', methods=['PUT', 'POST'])
def submit():
    job_id = uuid.uuid4().hex
    file = request.files['file_blob']

    exec_agent = json.loads(requests.get(f'http://{get_global("tracker_host")}:3000/assign_agent',
                                         params={'source': get_global('agent_name')}
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

    return response.json()
