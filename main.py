#!/usr/bin/env python3

import os
from utils import load_config

config = load_config('config.yaml')
byobu_command = f"byobu new-session -d -s mysession 'python3 bot.py' \\; new-window -t mysession 'python3 scheduler.py' \\; new-window -t mysession 'uvicorn subscribe:app --reload --host {config['subscription']['ip']} --ssl-keyfile db/cert/wlfvip.au1.store/sub-private.key --ssl-certfile /root/xray-bot/db/cert/wlfvip.au1.store/sub-cert.crt --port {config['subscription']['https_port']}'\\; new-window -t mysession 'uvicorn subscribe:app --reload --host {config['subscription']['ip']} --port {config['subscription']['http_port']}'"

os.system(byobu_command)
