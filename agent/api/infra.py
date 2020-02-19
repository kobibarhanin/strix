from flask import jsonify, Blueprint, render_template
import string
import random
import time
import os
from datetime import datetime

from infra.utils import logger, get_global, set_global, jobs_db
from infra.heartbeat import Heartbeat
from core.agent import Agent


infra_api = Blueprint('infra_api', __name__)
log = logger()


@infra_api.route('/heartbeat')
def heartbeat():
    beat = vars(Heartbeat())
    log.info(f'heartbeat -> {beat}')
    set_global('heartbeat_last', beat['timestamp'])
    return jsonify(beat)


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
    current_time = datetime.now()
    try:
        heartbeat_last = datetime.strptime(get_global('heartbeat_last'), "%Y-%m-%d %H:%M:%S.%f")
    except Exception:
        return {'status': 'disconnected'}
    if (current_time - heartbeat_last).seconds > 10:
        return {'status': 'disconnected'}
    else:
        return {'status': get_global('agent_status')}
