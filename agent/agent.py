from flask import Flask, request, send_file, jsonify, render_template
from subprocess import Popen, PIPE, STDOUT
import logging
import random
import string
import time
import datetime
import os
import uuid
import requests
import json

from infra.utils import logger, get_global, get_job, set_global, set_job, get_db, get_ip, copytree


app = Flask(__name__)
log = logger()


@app.route('/')
def get():
    return render_template('agent_view.html',
                           version=''.join(random.choices(string.ascii_uppercase + string.digits, k=10)),
                           agent=os.environ['AGENT_NAME'])


@app.route('/logs')
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


@app.route('/connectivity')
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


@app.route('/jobs')
def jobs():
    jobs = dict(get_db('jobs')[0])
    reply = dict()
    for id, job in jobs.items():
        if job['type'] == 'submitted':
            reply[id] = job
    return reply


@app.route('/heartbeat')
def heartbeat():
    set_global('heartbeat_last', str(time.time()))
    reply = {'name': get_global('agent_name'),
             'status': get_global('status'),
             'time': str(time.time())
             }
    log.info(f'heartbeat -> {reply}')
    return jsonify(reply)


@app.route('/get_report',  methods=['GET'])
def get_report():
    job_id = request.args.get('id')
    assigned_agent = get_job(job_id)['assigned_agent']
    return requests.get(f'http://{assigned_agent["url"]}:{assigned_agent["port"]}/report',
                        params={'job_id': job_id}).content.decode("ascii")


@app.route('/report',  methods=['GET'])
def report():
    job_id = request.args.get('job_id')
    job_status = get_job(job_id)['status']
    if job_status == 'completed':
        return send_file(f'/app/tasks/{job_id}/payload')
    else:
        return job_status


@app.route('/complete',  methods=['POST'])
def complete():
    task_id = request.args.get('task_id')
    completion_time = request.args.get('completion_time')
    set_job(task_id, 'status', 'completed')
    set_job(task_id, 'completion_time', completion_time)
    return 'success'


@app.route('/payload',  methods=['PUT', 'POST'])
def payload():
    filename = request.args.get('filename')
    task_id = request.args.get('task_id')
    submitter_name = request.args.get('submitter_name')
    submitter_url = request.args.get('submitter_url')
    submitter_port = request.args.get('submitter_port')
    submission_time = request.args.get('submission_time')
    file = request.files[filename]

    log.info(f'payload: {filename}, id: {task_id}')

    task_path = f'tasks/{task_id}'
    os.mkdir(task_path)
    job_path = f'tasks/{task_id}/job_app'
    os.mkdir(job_path)

    copytree('/app/job_app', job_path)

    set_job(task_id, 'status', 'received')
    set_job(task_id, 'start_time', time.time())
    set_job(task_id, 'type', 'execute')
    set_job(task_id, 'submitter_name', submitter_name)
    set_job(task_id, 'submitter_url', submitter_url)
    set_job(task_id, 'submitter_port', submitter_port)
    set_job(task_id, 'id', task_id)
    set_job(task_id, 'submission_time', submission_time)

    set_global('status', 'busy')

    # with open(f'{task_path}/{filename}', 'w') as blob:
    #     rd = file.read().decode('ascii')
    #     blob.write(rd)

    with open(f'{job_path}/job_pack/{filename}', 'w') as blob:
        rd = file.read().decode('ascii')
        blob.write(rd)


    cmd = f'bash infra/setup.sh {job_path}'
    Popen(cmd.split(), stderr=STDOUT, stdout=PIPE)


    # todo: this needs to run after setup and call the run() method implemented in the exe.py (noe exe_pack.py, just temporary)

    Popen(['python', 'executor.py', filename, task_id], stderr=STDOUT, stdout=PIPE)


    reply = {
        'agent': get_global('agent_name'),
        'port': get_global('agent_port'),
        'payload': filename,
        'submission_time': submission_time,
        'id': task_id,
    }

    return jsonify(reply)


@app.route('/execute', methods=['PUT','POST'])
def execute():

    task_id = uuid.uuid4().hex
    file = request.files['file_blob']

    exec_agent = json.loads(requests.get(f'http://{get_global("tracker_host")}:3000/assign_agent',
                              params={'source': get_global('agent_name')}
                              ).content.decode("ascii"))

    log.info(f'executing agent: {exec_agent["name"]} at {exec_agent["url"]}:{exec_agent["port"]}')

    set_job(task_id, 'type', 'submitted')
    set_job(task_id, 'status', 'submitted')
    set_job(task_id, 'assigned_agent', exec_agent)
    set_job(task_id, 'id', task_id)
    set_job(task_id, 'payload', file.filename)
    submission_time = str(datetime.datetime.now())
    set_job(task_id, 'submission_time', submission_time)

    response = requests.post(f'http://{exec_agent["url"]}:{exec_agent["port"]}/payload',
                             params={'filename': file.filename,
                                     'task_id': task_id,
                                     'submission_time': submission_time,
                                     'submitter_name': get_global('agent_name'),
                                     'submitter_url': get_global('agent_url'),
                                     'submitter_port': get_global('agent_port')
                                     },
                             files={file.filename: file})

    return response.json()


if __name__ == '__main__':

    set_global('agent_name', os.environ['AGENT_NAME'])
    set_global('agent_url', os.environ['AGENT_URL'])
    # set_global('agent_url', get_ip())
    port = os.environ['PORT'] if 'PORT' in os.environ else '5000'
    set_global('agent_port', port)
    set_global('status', 'ready')
    set_global('tracker_host', os.environ['TRACKER_HOST'] if 'TRACKER_HOST' in os.environ else 'tracker')

    app.run(debug=True, host='0.0.0.0', port=port)
