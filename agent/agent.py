from flask import Flask, request, send_file
from subprocess import Popen, PIPE, STDOUT
import logging
import time
import os
import yaml
import io
import uuid

app = Flask(__name__)
logging.basicConfig(filename="info.log", level=logging.INFO)


@app.route('/heartbeat')
def heartbeat():
    return get_conf('global', 'name') + ':' + \
           str(time.time()) + ':' + \
           get_conf('global', 'status')


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
    with open('info.log', 'a') as log:
        log.write(str(request.files)+'\n')
        log.write(str(request.headers)+'\n')

    file = request.files['file_blob']
    proc_id = uuid.uuid4().hex

    os.mkdir(proc_id)
    open(f'{proc_id}/{proc_id}_config.yaml', 'a').close()
    set_conf(f'{proc_id}/{proc_id}', 'status', 'received')

    set_conf('procs', proc_id, 'received')
    set_conf('global', 'status', 'busy')

    with open(f'{proc_id}/{file.filename}', 'w') as blob:
        rd = file.read().decode('ascii')
        blob.write(rd)

    Popen(['python', 'executor.py', file.filename, proc_id], stderr=STDOUT, stdout=PIPE)
    return f'received payload {file.filename}, executing under id: {proc_id}'


@app.route('/execute')
def execute_shell():
    cmd = request.args.get('cmd').split(',')
    logging.info(f'cmd:  {cmd}')
    process = Popen(cmd, stdout=PIPE)
    out, err = process.communicate()
    logging.info(f'res: {str(out)}')
    return out


def get_module_logger(mod_name):
    """
    To use this, do logger = get_module_logger(__name__)
    """
    logger = logging.getLogger(mod_name)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s [%(name)-12s] %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger


def get_conf(conf_type, conf):
    try:
        with open(f'{conf_type}_config.yaml', 'r') as stream:
            configs = yaml.safe_load(stream)
        return configs[conf]
    except Exception:
        print(f'No configuration for: {conf}')
        return None


def set_conf(conf_type, conf, val):
    with open(f'{conf_type}_config.yaml', 'r') as stream:
        configs = yaml.safe_load(stream)
    if configs == None:
        configs = dict()
    configs[conf] = val
    with io.open(f'{conf_type}_config.yaml', 'w') as outfile:
        yaml.dump(configs, outfile)


if __name__ == '__main__':
    configs = {'name': os.environ['AGENT_NAME'],
               'status': 'ready'}

    with io.open('global_config.yaml', 'w') as outfile:
        yaml.dump(configs, outfile)

    open('procs_config.yaml', 'a').close()

    app.run(debug=True, host='0.0.0.0')

