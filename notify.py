#!/usr/bin/python3

import os
import sys
import json
import subprocess

ha_conf_path = '/var/lib/cloudmonitor/ha.json'


if len(sys.argv) < 2 or (sys.argv[1] != 'master' and sys.argv[1] != 'slave' and sys.argv[1] != 'fault'):
    print(f'{os.path.basename(sys.argv[0])} (master|backup|fault)')
    sys.exit(1)

if sys.argv[1] == 'fault':
    subprocess.check_call('systemctl restart cloudmonitor', shell=True)
else:
    if os.path.exists(ha_conf_path):
        fp = open(ha_conf_path, 'w')
    else:
        fp = open(ha_conf_path, 'x')
    ha_obj = dict()
    ha_obj['master'] = True if sys.argv[1] == 'master' else False
    try:
        ha_data = json.dumps(ha_obj, indent=4, separators=(',', ': '))
        fp.write(ha_data)
    finally:
        fp.close()
