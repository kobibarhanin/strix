from flask import Flask, request, send_file, jsonify
from subprocess import Popen, PIPE, STDOUT
import logging
import time
import os
import uuid
import requests

from infra.utils import get_conf, set_conf, logger

app = Flask(__name__)
log = logger('kobi')

@app.route('/heartbeat')
def heartbeat():
    reply = {'name': get_conf('global', 'name'),
             'status': get_conf('global', 'status'),
             'time': str(time.time())
             }
    log.info(reply)
    return jsonify(reply)


@app.route('/report',  methods=['GET'])
def report():
    proc_uid = request.args.get('proc_uid')
    proc_status = get_conf('procs', proc_uid)
    if proc_status == 'completed':
        return send_file(f'{proc_uid}/{proc_uid}_payload')
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
    open(f'{task_path}/_config.yaml', 'a').close()
    set_conf(f'{task_path}/', 'status', 'received')
    set_conf('procs', task_id, 'received')
    set_conf('global', 'status', 'busy')

    with open(f'{task_path}/{filename}', 'w') as blob:
        rd = file.read().decode('ascii')
        blob.write(rd)

    Popen(['python', 'executor.py', filename, task_id], stderr=STDOUT, stdout=PIPE)

    reply = {
        'agent': get_conf('global','name'),
        'payload': filename,
        'id': task_id
    }
    return jsonify(reply)



@app.route('/execute', methods=['PUT'])
def execute():

    file = request.files['file_blob']

    agent_port = 5000

# todo - this needs to be done on two different machines
    response = requests.post(f'http://bitz_2:{agent_port}/payload',
                             params={'filename': file.filename},
                             files={file.filename: file})

    return response.json()



@app.route('/execute')
def execute_shell():
    cmd = request.args.get('cmd').split(',')
    logging.info(f'cmd:  {cmd}')
    process = Popen(cmd, stdout=PIPE)
    out, err = process.communicate()
    logging.info(f'res: {str(out)}')
    return out


if __name__ == '__main__':
    set_conf('global', 'name', os.environ['AGENT_NAME'])
    app.run(debug=True, host='0.0.0.0')
