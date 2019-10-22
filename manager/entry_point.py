from threading import Thread
from manager.agents_broker import sync
from manager.agents_view import app

thread = Thread(target=sync)
thread.start()

app.run(debug=False, host='0.0.0.0', port='3000')

# TODO:

# STATUS:
# TEST PAYLOAD -> curl  -X PUT -F file_blob=@/Users/kobarhan/pyexe.py "http://0.0.0.0:5000/payload"

# 2. add classes design
# 3. registration concept
# 4. fix docker logging issues
