from flask import Flask, request, send_file, jsonify
from subprocess import Popen, PIPE, STDOUT
import logging
import time
import os
import uuid

from utils import *

app = Flask(__name__)

logging.basicConfig(format='%(asctime)s %(message)s')
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


@app.route('/heartbeat')
def heartbeat():
    hb = {'name': get_conf('global', 'name'),
          'status': get_conf('global', 'status'),
          'time': str(time.time())
          }
    log.info(hb)
    return jsonify(hb)


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
    return f'Received payload: {filename}\nExecution id: {task_id}'


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
