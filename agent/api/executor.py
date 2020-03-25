from flask import request, jsonify, Blueprint, send_file
import jenkins

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

    try:
        agent = Agent(job.job_id)
        job_id = job.job_id

        reply = {
            'name': get_global('agent_name'),
            'url': get_global('agent_url'),
            'port': get_global('agent_port'),
            'payload': job.get("file_name"),
            'submission_time': job.get("submission_time"),
            'id': job_id,
        }

        if get_job(job_id)['job_status'] == 'aborted':
            agent.report(f'aborting job: {job_id}')
            log.info(f'aborting job: {job_id}')
            return jsonify(reply)


        agent.report(f'executing job: {job_id}')

        git_repo = job.get('git_repo')
        file_name = job.get('file_name')

        server = jenkins.Jenkins('http://jenkins:8080', username='admin', password='admin')

        job_definition = get_job_definition(git_repo, file_name)
        job_name = 'test'
        server.reconfig_job(job_name, job_definition)

        # set_job(job_id, {'job_status': 'installing'})
        # log.info(f'installing: {job.get("filename")} with id: {job_id}')
        # agent.report(f'installing {job.get("filename")}, for job: {job_id}')

        build_number = server.get_job_info(job_name)['nextBuildNumber']
        server.build_job(job_name)

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

        agent.complete()
        set_global('agent_status', 'connected')
        return jsonify(reply)

    except Exception as e:
        log.info(f'error: {e}')
        return f'error: {e}'

