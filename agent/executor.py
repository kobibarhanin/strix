import subprocess
import sys

from agent import set_conf

exe_file = sys.argv[1]
proc_id = sys.argv[2]

# update procs_config.yaml
set_conf('procs', proc_id, 'running')
# update task_config.yaml
set_conf(f'tasks/{proc_id}/', 'status', 'running')

import os
os.chdir('tasks')
os.chdir(proc_id)
subprocess.call(['python', exe_file, proc_id])
os.chdir('../../')

set_conf('procs', proc_id, 'completed')
set_conf(f'tasks/{proc_id}/', 'status', 'running')
set_conf(f'tasks/{proc_id}/', 'payload_path', f'tasks/{proc_id}/_payload')
set_conf('global', 'status', 'ready')