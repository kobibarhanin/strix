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
    payload = []
    for agent in agents.find():
        status = agent['status']
        if (datetime.now() - agent['timestamp']).total_seconds() > 10:
            status = 'disconnected'
        payload.append({'name': agent['name'],
                        'timestamp': agent['timestamp'],
                        'port': agent['port'],
                        'status': status})
    return jsonify(payload)


@app.route('/')
def get():
    return render_template('agents_view.html',
                           version=''.join(random.choices(string.ascii_uppercase + string.digits, k=10)))


@app.route('/payload', methods=['PUT'])
def payload():
    file = request.files['file_blob']
    params = {'filename': file.filename}

    agent_url = None
    agent_assigned = None
    for agent in agents.find():
        if agent['status'] == 'ready':
            agent_url = agent['port']
            agent_assigned = agent['name']
            continue

    if not agent_url:
        return 'unable to assign to agent'

    response = requests.post(f'http://0.0.0.0:{agent_url}/payload', params=params, files={file.filename: file})

    return f'Assigned to agent: {agent_assigned}\n' \
           f'{str(response.content.decode("utf-8"))}\n'


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port='3000')