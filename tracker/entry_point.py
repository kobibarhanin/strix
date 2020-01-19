from threading import Thread
from agents_broker import sync, register_agents
from agents_view import app

base_url = '0.0.0.0'
# agents_to_register = [{'name': 'bitz', 'url': base_url, 'port': 5000}, {'name': 'bitz_2', 'url': base_url, 'port': 5001}]
agents_to_register = [{'name': 'bitz', 'url': 'bitz', 'port': 5000}, {'name': 'bitz_2', 'url': 'bitz_2', 'port': 5000}]
register_agents(agents_to_register, drop=True)


thread = Thread(target=sync)
thread.start()

app.run(debug=False, host='0.0.0.0', port='3000')
