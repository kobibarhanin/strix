from flask import request, jsonify, Blueprint, send_file
import jenkins
import requests

from infra.utils import logger, get_global, get_job, set_global, set_job, get_db, get_job_definition
from infra.decorators import process_job
from infra.heartbeat import ExecutorHeartbeat
from core.agent import Agent


executor_api = Blueprint('executor_api', __name__)
log = logger()


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
    set_job(job_id, {'job_status': 'requested_abort'})
    Agent(job_id=job_id, role='execute').report_job(job_id, 'requested aborting')
    return {}


@executor_api.route('/report', methods=['GET'])
def report():
    job_id = request.args.get('job_id')
    job_status = get_job(job_id)['job_status']
    if job_status == 'completed':
        return send_file(f'/app/temp/{job_id}')
    else:
        return job_status


def check_abort(agent, job_id):
    if get_job(job_id)['job_status'] == 'requested_abort':
        set_job(job_id, {'job_status': 'aborted'})
        agent.log('aborted', report=True, job_id=job_id)
        return True
    return False


@executor_api.route('/execute', methods=['PUT', 'POST', 'GET'])
@process_job
def execute(job):
    try:
        job_id = job.job_id
        agent = Agent(job_id=job_id, role='execute')

        agent.report_job(job_id, 'executing')

        git_repo = job.get('git_repo')
        file_name = job.get('file_name')

        server = jenkins.Jenkins('http://jenkins:8080', username='admin', password='admin')

        job_definition = get_job_definition(git_repo, file_name)
        job_name = 'test'
        server.reconfig_job(job_name, job_definition)

        build_number = server.get_job_info(job_name)['nextBuildNumber']

        if check_abort(agent, job_id):
            set_global('agent_status', 'connected')
            return f'aborted job: {job_id}'

        server.build_job(job_name, {'BUILD_NAME': f'{get_global("agent_name")} - {job_id}'})

        build_started = False
        build_info = 'no build info'
        while not build_started:
            try:
                build_info = server.get_build_info(job_name, build_number)
                build_started = True
            except Exception:
                pass

        agent.log(build_info)

        build_finished = False
        while not build_finished:
            build_result = server.get_build_info(job_name, build_number)['result']
            if build_result is not None:
                build_finished = True

        if get_job(job_id)['job_status'] == 'requested_abort':
            agent.report_job(job_id, 'abort denied - late')

        try:
            result = requests.get(f'http://jenkins:8080/job/test/{build_number}/consoleText').content.decode("ascii")
            with open(f'/app/temp/{job_id}', 'w') as output:
                output.write(result)
            agent.log(f'job {job_id} result: {result}')
        except Exception as e:
            agent.log(f'unable to get results: {e}')

        agent.complete()
        set_global('agent_status', 'connected')
        return {}

    except Exception as e:
        log.info(f'error: {e}')
        return f'error: {e}'

