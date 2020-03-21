import logging
import socket
import os
import shutil
import pymongo


db = pymongo.MongoClient(f'mongodb://{os.environ["DB_HOST"]}:27017/')['agent']


def get_db(db_type):
    if db_type == 'global':
        return db['global'].find_one({'type': 'properties'})
    elif db_type == 'jobs':
        jobs = list(db['jobs'].find({}))
        for job in jobs:
            del job['_id']
        return jobs
    else:
        raise Exception('unsupported db')


def get_global(key):
    return db['global'].find_one({'type': 'properties'})[key]


def set_global(key, value):
    db['global'].update({'type': 'properties'}, {"$set": {key: value}})


def get_job(key):
    jobs = list(db['jobs'].find({}))
    for job in jobs:
        del job['_id']
        if job['id'] == key:
            return job


def set_job(jid, item):
    db_jobs = db['jobs']
    db_jobs.update({'id': jid}, {"$set": item}, upsert=True)


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


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def install_and_import(package):
    import importlib
    try:
        importlib.import_module(package)
    except ImportError:
        import pip
        pip.main(['install', package])
    finally:
        globals()[package] = importlib.import_module(package)


def is_installed():
    try:
        import job_pack
        return True
    except Exception:
        return False
