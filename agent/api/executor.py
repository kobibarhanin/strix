from flask import request, jsonify, Blueprint, send_file
from subprocess import Popen, PIPE, STDOUT
import time
import os


from infra.utils import logger, get_global, get_job, set_global, set_job, get_db, copytree, is_installed
from infra.decorators import process_job
from infra.heartbeat import ExecutorHeartbeat
from core.agent import Agent


executor_api = Blueprint('executor_api', __name__)
log = logger()


@executor_api.route('/jobs_executed')
def jobs_executed():
    reply = dict()
    for job in get_db('jobs'):
        if job['job_type'] == 'execute':
            reply[job['id']] = job
    return reply


@executor_api.route('/exec_heartbeat')
def exec_heartbeat():
    job_id = str(request.args.get('job_id'))
    try:
        heartbeat = vars(ExecutorHeartbeat(job_id))
        log.info(f'exec_heartbeat -> {heartbeat}')
        return jsonify(heartbeat)
    except Exception as e:
        log.info(f'error in exec_heartbeat: {e}')


@executor_api.route('/abort', methods=['GET'])
def abort():
    job_id = request.args.get('job_id')
    set_job(job_id, {'job_status': 'aborted'})
    agent = Agent(job_id)
    agent.report(f'requested aborting job: {job_id}')
    return {}


@executor_api.route('/report', methods=['GET'])
def report():
    job_id = request.args.get('job_id')
    job_status = get_job(job_id)['job_status']
    if job_status == 'completed':
        return send_file(f'/app/tasks/{job_id}/payload')
    else:
        return job_status


@executor_api.route('/execute', methods=['PUT', 'POST', 'GET'])
@process_job
def execute(job):

    git_repo = job.get('git_repo')
    file_name = job.get('file_name')

    job_definition = get_job_definition(git_repo, file_name)


    import jenkins
    server = jenkins.Jenkins('http://jenkins:8080', username='admin', password='admin')

    server.reconfig_job('test', job_definition)

    server.build_job('test')

    try:
        agent = Agent(job.job_id)
        job_id = job.job_id
        job.set('job_type', 'execute')

        # set_job(job_id, {'job_status': 'installing'})
        #
        # log.info(f'installing: {job.get("filename")} with id: {job_id}')
        # agent.report(f'installing {job.get("filename")}, for job: {job_id}')
        #
        # task_path = f'tasks/{job_id}'
        # os.mkdir(task_path)
        # job_path = f'tasks/{job_id}/job_app'
        # os.mkdir(job_path)
        # copytree('/app/job_app', job_path)

        # try:
        #     with open(f'{job_path}/job_pack/{job.get("filename")}', 'wb') as blob:
        #         rd = job.file.read()
        #         blob.write(rd)
        # except Exception as e:
        #     agent.report(f'error = {e}')

        # if str(job.get("filename")).endswith('.zip'):
        #     cmd = f'bash infra/setup.sh {job_path} unzip {job.get("filename")}'
        # else:
        #     cmd = f'bash infra/setup.sh {job_path}'
        # agent.report(f'executing setup: {cmd}')
        # Popen(cmd.split(), stderr=STDOUT, stdout=PIPE).communicate()
        #
        # time_ctr = 0
        # while not is_installed():
        #     time_ctr += 1
        #     time.sleep(1)
        #     if time_ctr >= 10:
        #         err_msg = f'failed installing job {job_id}, aborting'
        #         set_job(job_id, {'job_status': 'failed'})
        #         set_global('agent_status', 'connected')
        #         agent.report(err_msg)
        #         return
        #
        # set_job(job_id, {'job_status': 'installed'})

        reply = {
            'name': get_global('agent_name'),
            'url': get_global('agent_url'),
            'port': get_global('agent_port'),
            # 'payload': job.get("filename"),
            'payload': job.get("file_name"),
            'submission_time': job.get("submission_time"),
            'id': job_id,
        }

        # log.info(f'done installing {reply}')
        #
        # if get_job(job_id)['job_status'] == 'aborted':
        #     reply = {
        #         'name': get_global('agent_name'),
        #         'url': get_global('agent_url'),
        #         'port': get_global('agent_port'),
        #         # 'payload': job.get('filename'),
        #         'payload': job.get('file_name'),
        #         'submission_time': job.get('submission_time'),
        #         'id': job_id,
        #     }
        #
        #     agent.report(f'aborting job: {job_id}')
        #     log.info(f'aborting job: {job_id}')
        #
        #     return jsonify(reply)
        # else:
        #     agent.report(f'executing job: {job_id}')
        #     Popen(['python3', '/app/lib/executor.py', job_id], stderr=STDOUT, stdout=PIPE)

        return jsonify(reply)

    except Exception as e:
        log.info(f'error: {e}')
        return f'error: {e}'


def get_job_definition(repository, filename):
    import xml.etree.ElementTree

    et = xml.etree.ElementTree.parse('/app/job_templates/basic_job.xml')
    root = et.getroot()
    git_repo = root.find('.//url')
    file_name = root.find('.//scriptPath')

    git_repo.text = repository
    file_name.text = filename

    return xml.etree.ElementTree.tostring(root, 'utf-8').decode('utf-8')
