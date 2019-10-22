import subprocess
import sys

from agent import set_conf

exe_file = sys.argv[1]
proc_id = sys.argv[2]

open(f'{proc_id}_config.yaml', 'a').close()
set_conf(proc_id, 'status', 'running')

subprocess.call(['python', exe_file, proc_id])

set_conf(proc_id, 'status', 'completed')
set_conf(proc_id, 'payload_path', f'{proc_id}_payload')
set_conf('global', 'status', 'ready')