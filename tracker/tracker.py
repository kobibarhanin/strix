from datetime import datetime
import pymongo
from flask import Flask, jsonify, render_template, request
import random
import string


db_host = 'bitz_db'
agents = pymongo.MongoClient(f'mongodb://{db_host}:27017/')['agentsDb']['agent']

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
    timestamp = str(datetime.now())
    agent = agents.insert_one({'name': agent_name, 'timestamp': timestamp, 'port': '5000', 'url': agent_url, 'status': 'ready'})
    return str(agent.inserted_id)


@app.route('/assign_agent')
def assign_agent():
    for agent in agents.find():
        status = agent['status']
        name = agent['name']
        source = request.args.get('source')
        if status == 'ready' and not name == source:
            return agent['name']
    return None


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port='3000')