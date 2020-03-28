import sys
import requests
import json
import time
from datetime import datetime


# datetime.strptime(entry["timestamp"], '%a, %d %b %Y %H:%M:%S %Z')


def get_outline(job_id):
    response = requests.get('http://0.0.0.0:3000/outline',
                            params={
                                'job_id': job_id,
                            })

    for entry in json.loads(response.content):
        log_entry = f'{datetime.strptime(entry["timestamp"], "%a, %d %b %Y %H:%M:%S %Z").time()} | {entry["job_id"]} | {entry["agent_name"]} | {entry["role"]} - {entry["agent_log"]}'
        print(log_entry)


if __name__ == "__main__":

    if sys.argv[3] == 'outline':
        job_id = sys.argv[4]
        get_outline(job_id)

    if sys.argv[3] == 'test':
        response = requests.get('http://0.0.0.0:5000/submit',
                                params={
                                    'git_repo': 'https://github.com/kobibarhanin/Strix.git',
                                    'file_name': 'payloads/test_pipeline.groovy',
                                }).content
        response = json.loads(response)
        print(response)
        print('waiting for job completion')
        waiting = True
        while waiting:
            job_status = requests.get('http://0.0.0.0:5000/job_status',
                                      params={
                                          'job_id': response['job_id']
                                      }).content.decode("utf-8")
            if job_status != 'completed':
                sys.stdout.write('.')
                sys.stdout.flush()
                time.sleep(1)
            else:
                waiting = False

        sys.stdout.write('\n')
        get_outline(response['job_id'])
