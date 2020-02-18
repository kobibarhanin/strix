from flask import jsonify, Blueprint, render_template
import string
import random
import time
import os


from infra.utils import logger, get_global, set_global, jobs_db
from lib.agent import Agent


infra_api = Blueprint('infra_api', __name__)
log = logger()


@infra_api.route('/heartbeat')
def heartbeat():
    set_global('heartbeat_last', str(time.time()))
    reply = {'agent_name': get_global('agent_name'),
             'agent_status': get_global('agent_status'),
             'timestamp': str(time.time())
             }
    log.info(f'heartbeat -> {reply}')
    return jsonify(reply)


@infra_api.route('/disable_agent')
def disable_agent():
    set_global('agent_status', 'disabled')
    for job in jobs_db:
        if job['status'] != 'completed':
            agent = Agent(job['id'])
            assign_agent = job['assign_agent']
            agent.deorchestrate(assign_agent['url'], assign_agent['port'])
    return {}


@infra_api.route('/')
def get():
    return render_template('agent_view.html',
                           version=''.join(random.choices(string.ascii_uppercase + string.digits, k=10)),
                           agent=os.environ['AGENT_NAME'])


@infra_api.route('/logs')
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


@infra_api.route('/connectivity')
def connectivity():
    current_time = time.time()
    try:
        heartbeat_last = float(get_global('heartbeat_last'))
    except Exception:
        return {'status': 'disconnected'}
    if current_time - heartbeat_last > 10:
        return {'status': 'disconnected'}
    else:
        return {'status': get_global('agent_status')}
