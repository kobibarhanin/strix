import sys
import requests
import json
from datetime import datetime

# datetime.strptime(entry["timestamp"], '%a, %d %b %Y %H:%M:%S %Z')

if __name__ == "__main__":

    job_id = sys.argv[3]

    response = requests.get('http://0.0.0.0:3000/outline',
                            params={
                                'job_id': job_id,
                            })

    for entry in json.loads(response.content):
        log_entry = f'{datetime.strptime(entry["timestamp"], "%a, %d %b %Y %H:%M:%S %Z").time()} | {entry["job_id"]} | {entry["agent_name"]} | {entry["role"]} - {entry["agent_log"]}'
        print(log_entry)

