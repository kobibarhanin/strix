import logging
import socket

from jsondb.db import Database

global_db = Database('/app/global.db')
jobs_db = Database('/app/jobs.db')


def get_db(db):
    if db == 'global':
        return global_db
    elif db == 'jobs':
        return jobs_db
    else:
        raise Exception('unsupported db')


def get_global(key):
    return global_db[key]


def set_global(key, value):
    global_db[key] = value


def get_job(key):
    return jobs_db[key]


def set_job(jid, key, value):
    if not jobs_db[jid]:
        jobs_db[jid] = {key: value}
    else:
        tmp = jobs_db[jid]
        tmp[key] = value
        jobs_db[jid] = tmp


def logger(name=None):
    logging.basicConfig(filename='agent.log', format='%(asctime)s %(message)s')
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    return log


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP