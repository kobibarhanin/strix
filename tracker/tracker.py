from datetime import datetime
import pymongo
from flask import Flask, jsonify, render_template, request
import random
import string
import os

# TODO: this needs to be initialized once in the init.py
# from . import agents, logs_stream
db_host = os.environ['DB_CTX'] if 'DB_CTX' in os.environ else 'bitz_db'
agents = pymongo.MongoClient(f'mongodb://{db_host}:27017/')['agentsDb']['agent']
logs_stream = pymongo.MongoClient(f'mongodb://{db_host}:27017/')['agentsDb']['logs_stream']

app = Flask(__name__)


@app.route('/')
def get():
    return render_template('tracker_view.html',
                           version=''.join(random.choices(string.ascii_uppercase + string.digits, k=10)))


@app.route('/agents')
def get_agents():
    agents_pool = []
    for agent in agents.find():
        status = agent['status']
        if (datetime.now() - agent['timestamp']).total_seconds() > 10:
            status = 'disconnected'
        agents_pool.append({'name': agent['name'],
                            'timestamp': agent['timestamp'],
                            'port': agent['port'],
                            'status': status})
    return jsonify(agents_pool)


@app.route('/register_agent')
def register_agent():
    agent_name = request.args.get('agent_name')
    agent_url = request.args.get('agent_url')
    agent_port = request.args.get('agent_port')
    timestamp = datetime.now()
    agent = agents.insert_one({'name': agent_name,
                               'timestamp': timestamp,
                               'port': agent_port,
                               'url': agent_url,
                               'status': 'registered'})
    return str(agent.inserted_id)


@app.route('/unregister_agent')
def unregister_agent():
    agent_name = request.args.get('agent_name')
    agent = agents.delete_one({'name': agent_name})
    return str(agent)


# TODO: temporary random executors and orchestrators assignment

@app.route('/assign_agents')
def assign_agents():
    source = request.args.get('source')
    required = int(request.args.get('required'))
    restrictions = [source]
    if 'orchestrator' in request.args:
        orchestrator = request.args.get('orchestrator')
        restrictions.append(orchestrator)

    agents_assigned = []
    for i in range(0, required):
        assigned = assign_agent(restrictions)
        agents_assigned.append(assigned)
        restrictions.append(assigned["name"])


    return jsonify(agents_assigned)


def assign_agent(restrictions):
    while True:
        agents_pool = list(agents.find())
        agent = random.choice(agents_pool)
        status = agent['status']
        name = agent['name']
        if status == 'ready' and name not in restrictions:
            return {'name': agent['name'], 'port': agent['port'], 'url': agent['url']}

# @app.route('/assign_executor')
# def assign_agent():
#     for agent in agents.find():
#         status = agent['status']
#         name = agent['name']
#         source = request.args.get('source')
#         if status == 'ready' and not name == source:
#             return jsonify({'name': agent['name'], 'port': agent['port'], 'url': agent['url']})
#     return None


# @app.route('/assign_orchestrator')
# def assign_orchestrator():
#     for agent in agents.find():
#         status = agent['status']
#         name = agent['name']
#         source = request.args.get('source')
#         orchestrator = request.args.get('orchestrator')
#         if status == 'ready' and not name == source and not name == orchestrator:
#             return jsonify({'name': agent['name'], 'port': agent['port'], 'url': agent['url']})
#     return None


@app.route('/log_report')
def log_report():
    agent_name = request.args.get('agent_name')
    # agent_url = request.args.get('agent_url')
    # agent_port = request.args.get('agent_port')
    agent_log = request.args.get('agent_log')
    timestamp = datetime.now()
    log = logs_stream.insert_one({'name': agent_name,
                               'timestamp': timestamp,
                               # 'port': agent_port,
                               # 'url': agent_url,
                               'log': agent_log})
    return str(log.inserted_id)


# TODO - need to reverse logs sent to tracker
@app.route('/log_export')
def log_export():
    logs = []
    for log in logs_stream.find():
        logs.append(f'{log["timestamp"]} - {log["name"]}: {log["log"]}\n')
    return jsonify(list(reversed(logs)))


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port='3000')
