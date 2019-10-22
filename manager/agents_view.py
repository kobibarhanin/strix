from datetime import datetime
import pymongo
from flask import Flask, jsonify, render_template
import random
import string


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


if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port='3000')