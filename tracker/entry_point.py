from threading import Thread
from agents_broker import sync
from agents_view import app

thread = Thread(target=sync)
thread.start()

app.run(debug=False, host='0.0.0.0', port='3000')
