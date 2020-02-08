from flask import jsonify, Blueprint
import time

from infra.utils import logger, get_global, set_global


infra_api = Blueprint('infra_api', __name__)
log = logger()


@infra_api.route('/heartbeat')
def heartbeat():
    set_global('heartbeat_last', str(time.time()))
    reply = {'name': get_global('agent_name'),
             'status': get_global('status'),
             'time': str(time.time())
             }
    log.info(f'heartbeat -> {reply}')
    return jsonify(reply)
