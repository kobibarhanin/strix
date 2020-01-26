import yaml
import io
import logging

from jsondb.db import Database

global_db = Database('/app/global.db')
jobs_db = Database('/app/jobs.db')


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
    logging.basicConfig(format='%(asctime)s %(message)s')
    log = logging.getLogger(name)
    log.setLevel(logging.DEBUG)
    return log
