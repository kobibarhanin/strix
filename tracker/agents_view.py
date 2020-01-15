from datetime import datetime
import pymongo
from flask import Flask, jsonify, render_template, request
import random
import string
import requests


agents = pymongo.MongoClient("mongodb://localhost:27017/")['agentsDb']['agent']
app = Flask(__name__)


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


@app.route('/assign_agent')
def assign_agent():
    for agent in agents.find():
        status = agent['status']
        name = agent['name']
        source = request.args.get('source')
        if status == 'ready' and not name == source:
            return agent['name']
    return None


@app.route('/')
def get():
    return render_template('agents_view.html',
                           version=''.join(random.choices(string.ascii_uppercase + string.digits, k=10)))


@app.route('/payload', methods=['PUT'])
def payload():
    file = request.files['file_blob']

    agent_url = None
    for agent in agents.find():
        if agent['status'] == 'ready':
            agent_port = agent['port']
            agent_url = agent['url']
            continue

    if not agent_url:
        return 'unable to assign to agent'

    response = requests.post(f'http://{agent_url}:{agent_port}/payload',
                             params={'filename': file.filename},
                             files={file.filename: file})

    return response.json()


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port='3000')