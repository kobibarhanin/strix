from flask import Flask, request, send_file, jsonify, render_template
from subprocess import Popen, PIPE, STDOUT
import logging
import random
import string
import time
import os
import uuid
import requests
from jsondb.db import Database

from infra.utils import logger, get_global, get_job, set_global, set_job

app = Flask(__name__)
log = logger('kobi')

global_db = Database("global.db")
jobs_db = Database("jobs.db")


@app.route('/')
def get():
    return render_template('agent_view.html',
                           version=''.join(random.choices(string.ascii_uppercase + string.digits, k=10)),
                           agent=os.environ['AGENT_NAME'])

# @app.route('/home')
# def home():



@app.route('/heartbeat')
def heartbeat():
    reply = {'name': get_global('agent_name'),
             'status': get_global('status'),
             'time': str(time.time())
             }
    log.info(reply)
    return jsonify(reply)


@app.route('/report',  methods=['GET'])
def report():
    proc_uid = request.args.get('proc_uid')
    proc_status = get_job(proc_uid)['status']
    if proc_status == 'completed':
        return send_file(f'/app/tasks/{proc_uid}/_payload')
    else:
        return proc_status


@app.route('/payload',  methods=['PUT', 'POST'])
def payload():
    filename = request.args.get('filename')
    file = request.files[filename]
    task_id = uuid.uuid4().hex
    log.info(f'payload: {filename}, id: {task_id}')

    task_path = f'tasks/{task_id}'
    os.mkdir(task_path)

    set_job(task_id, 'status', 'received')
    set_job(task_id, 'start_time', time.time())

    set_global('status', 'busy')

    with open(f'{task_path}/{filename}', 'w') as blob:
        rd = file.read().decode('ascii')
        blob.write(rd)

    Popen(['python', 'executor.py', filename, task_id], stderr=STDOUT, stdout=PIPE)

    reply = {
        'agent': get_global('agent_name'),
        'payload': filename,
        'id': task_id
    }
    return jsonify(reply)



@app.route('/execute', methods=['PUT','POST'])
def execute():

    file = request.files['file_blob']

    agent_port = 5000

    PARAMS = {'source': get_global('agent_name')}
    log.info(f'params: {PARAMS}')

    agent_name = requests.get(f'http://tracker:3000/assign_agent', params = PARAMS)
    log.info(f'executing agent: {agent_name.content.decode("ascii")}')

    response = requests.post(f'http://{agent_name.content.decode("ascii")}:{agent_port}/payload',
                             params={'filename': file.filename},
                             files={file.filename: file})

    return response.json()


# @app.route('/execute')
# def execute_shell():
#     cmd = request.args.get('cmd').split(',')
#     logging.info(f'cmd:  {cmd}')
#     process = Popen(cmd, stdout=PIPE)
#     out, err = process.communicate()
#     logging.info(f'res: {str(out)}')
#     return out


if __name__ == '__main__':
    set_global('agent_name', os.environ['AGENT_NAME'])
    set_global('status', 'ready')
    app.run(debug=True, host='0.0.0.0')
