from threading import Thread
from agents_broker import sync
from tracker import app

thread = Thread(target=sync)
thread.start()

app.run(debug=False, host='0.0.0.0', port='3000')
