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


def get_job_definition(repository, filename):
    import xml.etree.ElementTree

    et = xml.etree.ElementTree.parse('/app/job_templates/basic_job.xml')
    root = et.getroot()
    git_repo = root.find('.//url')
    file_name = root.find('.//scriptPath')

    git_repo.text = repository
    file_name.text = filename

    return xml.etree.ElementTree.tostring(root, 'utf-8').decode('utf-8')
