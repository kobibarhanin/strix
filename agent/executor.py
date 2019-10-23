import subprocess
import sys

from agent import set_conf

exe_file = sys.argv[1]
proc_id = sys.argv[2]

set_conf('procs', proc_id, 'running')
set_conf(f'{proc_id}/{proc_id}', 'status', 'running')

import os
os.chdir(proc_id)
subprocess.call(['python', exe_file, proc_id])
os.chdir('../')

set_conf('procs', proc_id, 'completed')
set_conf(f'{proc_id}/{proc_id}', 'status', 'completed')
set_conf(f'{proc_id}/{proc_id}', 'payload_path', f'{proc_id}/{proc_id}_payload')
set_conf('global', 'status', 'ready')